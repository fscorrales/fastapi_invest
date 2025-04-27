__all__ = ["WSMarketDataService", "WSMarketDataServiceDependency"]

import asyncio
from dataclasses import dataclass
from typing import Annotated

import orjson
import pandas as pd
import websockets
from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import format_params, get_token
from ..schemas import (
    ConnectPrimary,
    PrimaryCredentials,
    WSMarketDataParams,
)


# -------------------------------------------------
@dataclass
class WSMarketDataService:
    market_data_df: pd.DataFrame
    task: asyncio.Task = None
    """
    WebSocket Market Data Service
    """

    # -------------------------------------------------
    async def sync_ws_market_data_from_primary(
        self, credentials: PrimaryCredentials, params: WSMarketDataParams = None
    ) -> str:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_primary = await get_token(
                    credentials.username,
                    credentials.password,
                    credentials.url,
                    httpxAsyncClient=c,
                )

                self.task = asyncio.create_task(
                    self._websocket_receiver(
                        primary=connect_primary,
                        params=params,
                        url=credentials.url,
                    )
                )

            except ValidationError as e:
                logger.error(f"Validation Error: {e}")
                raise HTTPException(
                    status_code=400, detail="Invalid response format from Primary"
                )
            except Exception as e:
                logger.error(f"Error during report processing: {e}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials or unable to authenticate",
                )

    async def disconnect(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    async def _websocket_receiver(
        self, primary: ConnectPrimary, params: WSMarketDataParams, url: str = None
    ):
        if url is None:
            url = primary.websocket_url
        h = {"X-Auth-Token": primary.x_auth_token}

        # Params para el mensaje de suscripción
        params = format_params(params)
        msg_dict = params.model_dump(mode="json", exclude_none=True)

        print(f"📡 Conectando a WebSocket {url}")
        async with websockets.connect(url, extra_headers=h) as ws:
            await ws.send(orjson.dumps(msg_dict))
            print("📡 Suscripción enviada.")

            try:
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=10)
                        print("📥 Recibido:", message)
                        self._handle_message(message)
                    except asyncio.TimeoutError:
                        print("⏳ No se recibió respuesta en 10 segundos.")

            except websockets.exceptions.ConnectionClosed:
                print("❌ Conexión cerrada.")
            except asyncio.CancelledError:
                print("🛑 Stream cancelado.")
                raise
            finally:
                await ws.close()

    def _handle_message(self, message: str):
        try:
            data = orjson.loads(message)
            if data.get("type") != "Md":
                return  # ignorar si no es Market Data

            symbol = data["instrumentId"]["symbol"]
            timestamp = data["timestamp"]
            price = None

            market_data = data.get("marketData", {})
            if "OP" in market_data and market_data["OP"] is not None:
                price = market_data["OP"]
            elif "CL" in market_data and isinstance(market_data["CL"], dict):
                price = market_data["CL"].get("price")

            if price is not None:
                # Actualizar o insertar
                self.market_data_df.loc[symbol] = {
                    "symbol": symbol,
                    "price": price,
                    "timestamp": timestamp,
                }

        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")

    def get_dataframe(self) -> pd.DataFrame:
        return self.market_data_df.copy()


# # Singleton de WebSocketManager
# primary_ws_manager = WSMarketDataService()


# def get_primary_ws_manager() -> WSMarketDataService:
#     return primary_ws_manager


WSMarketDataServiceDependency = Annotated[WSMarketDataService, Depends()]
