__all__ = ["WSMarketDataService", "WSMarketDataServiceDependency"]

import asyncio
from dataclasses import dataclass, field
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


def _init_market_data_df():
    df = pd.DataFrame(
        columns=[
            "timestamp",
            "lo",
            "nv",
            "ev",
            "op",
            "hi",
            "tv",
            "se",
            "oi",
            "iv",
            "acp",
            "bi",
            "of",
            "cl_price",
            "cl_date",
            "la_price",
            "la_size",
            "la_date",
        ]
    )
    df.index.name = "symbol"
    return df


# -------------------------------------------------
@dataclass
class WSMarketDataService:
    market_data_df: pd.DataFrame = field(default_factory=_init_market_data_df)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
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
                    websocket_url="wss://api.veta.xoms.com.ar",
                    httpxAsyncClient=c,
                )

                self.task = asyncio.create_task(
                    self._websocket_receiver(primary=connect_primary, params=params)
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

            return {"message": "WebSocket conectado."}

    # -------------------------------------------------
    async def disconnect(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    # -------------------------------------------------
    async def _websocket_receiver(
        self, primary: ConnectPrimary, params: WSMarketDataParams
    ):
        url = primary.websocket_url
        h = {"X-Auth-Token": primary.x_auth_token}

        # Params para el mensaje de suscripción
        msg_dict = format_params(params)
        # msg_dict = params.model_dump(mode="json", exclude_none=True)

        print(f"📡 Conectando a WebSocket {url}")
        async with websockets.connect(url, extra_headers=h) as ws:
            await ws.send(orjson.dumps(msg_dict).decode())
            print("📡 Suscripción enviada.")

            try:
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=10)
                        logger.info("📥 Recibido:", message)
                        await self._handle_message(message)
                    except asyncio.TimeoutError:
                        logger.error("⏳ No se recibió respuesta en 10 segundos.")

            except websockets.exceptions.ConnectionClosed:
                logger.info("❌ Conexión cerrada.")
            except asyncio.CancelledError:
                logger.error("🛑 Stream cancelado.")
                raise
            finally:
                await ws.close()

    # -------------------------------------------------
    async def _handle_message(self, message: str):
        try:
            data = orjson.loads(message)

            if data.get("type") != "Md":
                return  # Solo procesamos Market Data

            instrument = data["instrumentId"]["symbol"]
            timestamp = data.get("timestamp")
            md = data.get("marketData", {})

            # Armamos el registro
            record = {
                "timestamp": timestamp,
                "lo": md.get("LO"),
                "nv": md.get("NV"),
                "ev": md.get("EV"),
                "op": md.get("OP"),
                "hi": md.get("HI"),
                "tv": md.get("TV"),
                "se": md.get("SE"),
                "oi": md.get("OI"),
                "iv": md.get("IV"),
                "acp": md.get("ACP"),
                "bi": md.get("BI", []),
                "of": md.get("OF", []),
                "cl_price": None,
                "cl_date": None,
                "la_price": None,
                "la_size": None,
                "la_date": None,
            }

            if cl := md.get("CL"):
                record["cl_price"] = cl.get("price")
                record["cl_date"] = cl.get("date")

            if la := md.get("LA"):
                record["la_price"] = la.get("price")
                record["la_size"] = la.get("size")
                record["la_date"] = la.get("date")

            async with self.lock:
                if instrument in self.market_data_df.index:
                    # ✅ Solo actualizamos si el timestamp recibido es más reciente
                    existing_timestamp = self.market_data_df.at[instrument, "timestamp"]
                    if timestamp > existing_timestamp:
                        for key, value in record.items():
                            self.market_data_df.at[instrument, key] = value
                else:
                    # No existe -> lo agregamos
                    new_row = pd.DataFrame([record], index=[instrument])
                    self.market_data_df = pd.concat([self.market_data_df, new_row])

        except Exception as e:
            print(f"Error procesando mensaje: {e}")

    # -------------------------------------------------
    def get_dataframe(self) -> pd.DataFrame:
        logger.info(f"Registros actuales en DataFrame: {len(self.market_data_df)}")
        return self.market_data_df.copy()


# Singleton de WebSocketManager
primary_ws_manager = WSMarketDataService()


def get_primary_ws_manager() -> WSMarketDataService:
    return primary_ws_manager


WSMarketDataServiceDependency = Annotated[
    WSMarketDataService, Depends(get_primary_ws_manager)
]
