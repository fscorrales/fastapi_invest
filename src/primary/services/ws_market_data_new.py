__all__ = ["WSMarketDataService", "WSMarketDataServiceDependency"]

import asyncio
from dataclasses import dataclass, field
from typing import Annotated, List, Optional

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
    queue = asyncio.Queue()
    data: List[dict] = field(default_factory=list)
    """
    WebSocket Market Data Service
    """


    async def stream_market_data(self, credentials: PrimaryCredentials, params: WSMarketDataParams = None):
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

                msg_dict = format_params(params)
                headers = {"X-Auth-Token": connect_primary.x_auth_token}

                async with websockets.connect(connect_primary.websocket_url, extra_headers=headers) as ws:
                    await ws.send(orjson.dumps(msg_dict).decode())
                    print("📡 Suscripción enviada correctamente")

                    consumer = asyncio.create_task(self._process_messages())
                    producer = asyncio.create_task(self._receive_messages(ws))

                    await asyncio.gather(producer, consumer)

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

    async def _receive_messages(self, ws):
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=10)
                print(f"📥 Recibido: {raw}")
                await self.queue.put(raw)
            except asyncio.TimeoutError:
                print("⏳ Timeout esperando mensajes")
            except websockets.exceptions.ConnectionClosed:
                print("❌ Conexión cerrada")
                break
            except asyncio.CancelledError:
                print("🛑 Recepción cancelada")
                break

    async def _process_messages(self):
        while True:
            raw = await self.queue.get()
            try:
                msg = orjson.loads(raw)
                if msg.get("type") == "Md":
                    parsed = self._parse_message(msg)
                    if parsed:
                        self.data.append(parsed)
            except Exception as e:
                print(f"⚠️ Error procesando mensaje: {e}")
            finally:
                self.queue.task_done()

    def _parse_message(self, message: dict) -> Optional[dict]:
        """Parsea un mensaje 'Md' y lo convierte en dict"""
        try:
            instrument = message["instrumentId"]["symbol"]
            price = message["marketData"].get("OP")
            timestamp = message.get("timestamp")
            return {
                "symbol": instrument,
                "price": price,
                "timestamp": timestamp
            }
        except Exception as e:
            print(f"⚠️ Error parseando mensaje: {e}")
            return None

    def get_dataframe(self) -> pd.DataFrame:
        """Devuelve los datos como un DataFrame"""
        if not self.data:
            return pd.DataFrame()
        return pd.DataFrame(self.data)


# Singleton de WebSocketManager
primary_ws_manager = WSMarketDataService()


def get_primary_ws_manager() -> WSMarketDataService:
    return primary_ws_manager


WSMarketDataServiceDependency = Annotated[
    WSMarketDataService, Depends(get_primary_ws_manager)
]
