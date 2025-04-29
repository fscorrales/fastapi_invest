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
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    task: Optional[asyncio.Task] = None
    """
    WebSocket Market Data Service
    """

    # -------------------------------------------------
    async def stream_market_data(
        self, credentials: PrimaryCredentials, params: WSMarketDataParams = None
    ):
        self.task = asyncio.create_task(self.connect(credentials, params))
        return {"message": "WebSocket conectado."}

    # -------------------------------------------------
    async def connect(
        self, credentials: PrimaryCredentials, params: WSMarketDataParams = None
    ):
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

                async with websockets.connect(
                    connect_primary.websocket_url, extra_headers=headers
                ) as ws:
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

    # -------------------------------------------------
    async def _receive_messages(self, ws):
        self._message_counter = 0  # Inicializamos el contador

        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=10)
                self._message_counter += 1

                # Mostrar el mensaje completo solo cada 50 veces
                if self._message_counter % 50 == 0:
                    logger.debug(
                        f"📥 Recibido mensaje #{self._message_counter}: {raw[:300]}..."
                    )
                # else:
                #     # Mostrar resumen si es mensaje de tipo 'Md'
                #     try:
                #         msg = orjson.loads(raw)
                #         if msg.get("type") == "Md":
                #             symbol = msg["instrumentId"]["symbol"]
                #             op = msg.get("marketData", {}).get("OP")
                #             logger.debug(f"📥 {symbol}: OP={op}")
                #     except Exception:
                #         pass  # Ignorar si no se puede parsear

                await self.queue.put(raw)

            except asyncio.TimeoutError:
                logger.warning("⏳ Timeout esperando mensajes")
            except websockets.exceptions.ConnectionClosed:
                logger.warning("❌ Conexión cerrada")
                break
            except asyncio.CancelledError:
                logger.info("🛑 Recepción cancelada")
                break

    # -------------------------------------------------
    async def _process_messages(self):
        while True:
            raw = await self.queue.get()
            try:
                await self._handle_message(raw)
            except Exception as e:
                print(f"⚠️ Error procesando mensaje: {e}")
            finally:
                self.queue.task_done()

    # # -------------------------------------------------
    # def _parse_message(self, message: dict) -> Optional[dict]:
    #     """Parsea un mensaje 'Md' y lo convierte en dict"""
    #     try:
    #         instrument = message["instrumentId"]["symbol"]
    #         price = message["marketData"].get("OP")
    #         timestamp = message.get("timestamp")
    #         return {"symbol": instrument, "price": price, "timestamp": timestamp}
    #     except Exception as e:
    #         print(f"⚠️ Error parseando mensaje: {e}")
    #         return None

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
    async def disconnect(self):
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                print("🛑 Tarea de WebSocket cancelada correctamente.")
        self.task = None

    # -------------------------------------------------
    def get_dataframe(self) -> pd.DataFrame:
        """Devuelve los datos como un DataFrame"""
        return self.market_data_df.copy()

    # -------------------------------------------------
    def reset_dataframe(self):
        """Limpia el DataFrame y la lista de datos acumulados"""
        self.market_data_df = _init_market_data_df()


# Singleton de WebSocketManager
primary_ws_manager = WSMarketDataService()


# -------------------------------------------------
def get_primary_ws_manager() -> WSMarketDataService:
    return primary_ws_manager


WSMarketDataServiceDependency = Annotated[
    WSMarketDataService, Depends(get_primary_ws_manager)
]
