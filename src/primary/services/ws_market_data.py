__all__ = ["WSMarketDataService", "WSMarketDataServiceDependency"]

import asyncio
from dataclasses import dataclass, field
from typing import Annotated, Optional, Union

import orjson
import pandas as pd
import websockets
from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ...utils import safe_get, safe_list_get
from ..handlers import format_params, get_token
from ..schemas import (
    PrimaryCredentials,
    WSMarketDataParams,
    WSMarketDataSubscription,
)


def _init_market_data_df():
    dtypes = {
        "timestamp": "int64",
        "last_price": "float64",
        "last_size": "float64",
        "bid_price": "float64",
        "bid_size": "float64",
        "offer_price": "float64",
        "offer_size": "float64",
        "notional_value": "float64",
        "effective_value": "float64",
        "open": "float64",
        "close_prev": "float64",
        "high": "float64",
        "low": "float64",
        "tv": "float64",
        "se": "float64",
        "oi": "float64",
        "iv": "float64",
        "acp": "float64",
    }

    df = pd.DataFrame({col: pd.Series(dtype=typ) for col, typ in dtypes.items()})
    df.index.name = "instrument"
    return df


# -------------------------------------------------
@dataclass
class WSMarketDataService:
    market_data_df: pd.DataFrame = field(default_factory=_init_market_data_df)
    queue = asyncio.Queue()
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    task: Optional[asyncio.Task] = None
    is_running: bool = False
    """
    WebSocket Market Data Service
    """

    # -------------------------------------------------
    async def stream_market_data(
        self,
        credentials: PrimaryCredentials,
        params: Union[WSMarketDataSubscription, WSMarketDataParams] = None,
    ):
        self.task = asyncio.create_task(self.connect(credentials, params))
        return {"message": "WebSocket conectado."}

    # -------------------------------------------------
    async def connect(
        self,
        credentials: PrimaryCredentials,
        params: Union[WSMarketDataSubscription, WSMarketDataParams] = None,
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

                if isinstance(params, WSMarketDataParams):
                    params = format_params(params)

                msg_dict = params.model_dump(mode="json", exclude_none=True)
                headers = {"X-Auth-Token": connect_primary.x_auth_token}

                self.ws = await websockets.connect(
                    connect_primary.websocket_url, extra_headers=headers
                )
                await self.ws.send(orjson.dumps(msg_dict).decode())
                print("📡 Suscripción enviada correctamente")

                # Guardamos las tareas para posible cancelación luego
                self.is_running = True
                self.consumer_task = asyncio.create_task(self._process_messages())
                self.producer_task = asyncio.create_task(
                    self._receive_messages(self.ws)
                )

                logger.info(
                    "[WSMarketDataService] WebSocket conectado y tareas lanzadas"
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
    async def _receive_messages(self, ws):
        self._message_counter = 0  # Inicializamos el contador

        try:
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=10)
                    self._message_counter += 1

                    # Mostrar el mensaje completo solo cada 50 veces
                    if self._message_counter % 50 == 0:
                        logger.debug(
                            f"📥 Recibido mensaje #{self._message_counter}: {raw[:300]}..."
                        )

                    await self.queue.put(raw)
                except asyncio.TimeoutError:
                    logger.warning("⏳ Timeout esperando mensajes. Reintentando...")
                    continue  # ⬅️ importante para seguir escuchando

        except asyncio.CancelledError:
            logger.info("🛑 _receive_messages fue cancelado")
            raise
        except websockets.exceptions.ConnectionClosed:
            logger.warning("❌ Conexión cerrada")

    # -------------------------------------------------
    async def _process_messages(self):
        try:
            while True:
                raw = await self.queue.get()
                try:
                    await self._handle_message(raw)
                except Exception as e:
                    print(f"⚠️ Error procesando mensaje: {e}")
                finally:
                    self.queue.task_done()
        except asyncio.CancelledError:
            logger.info("🛑 _process_messages fue cancelado")
            raise

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
                "notional_value": md.get("NV"),
                "effective_value": md.get("EV"),
                "open": md.get("OP"),
                "close_prev": safe_get(md.get("CL"), ["price"]),
                "high": md.get("HI"),
                "low": md.get("LO"),
                "tv": md.get("TV"),
                "se": md.get("SE"),
                "oi": md.get("OI"),
                "iv": md.get("IV"),
                "acp": md.get("ACP"),
                # "last_price": md.get("LA", {}).get("price"),
                # "last_size": md.get("LA", {}).get("size"),
                "last_price": safe_get(md.get("LA"), ["price"]),
                "last_size": safe_get(md.get("LA"), ["size"]),
                "bid_price": safe_list_get(md.get("BI"), 0, "price"),
                "bid_size": safe_list_get(md.get("BI"), 0, "size"),
                "offer_price": safe_list_get(md.get("OF"), 0, "price"),
                "offer_size": safe_list_get(md.get("OF"), 0, "size"),
            }

            async with self.lock:
                new_row = pd.DataFrame([record], index=[instrument])

                if instrument in self.market_data_df.index:
                    existing_timestamp = self.market_data_df.at[instrument, "timestamp"]
                    if timestamp > existing_timestamp:
                        # Reemplazamos toda la fila
                        self.market_data_df.loc[instrument] = new_row.loc[instrument]
                else:
                    if not new_row.isna().all(axis=1).all():
                        self.market_data_df.loc[instrument] = new_row.loc[instrument]
                    # self.market_data_df = pd.concat(
                    #     [df for df in [self.market_data_df, new_row] if not df.empty]
                    # )
                    # self.market_data_df = pd.concat([self.market_data_df, new_row])

        except Exception as e:
            print(f"⚠️ Mensaje inválido: {md}")
            print(f"Error procesando mensaje: {e}")

    # -------------------------------------------------
    async def disconnect(self):
        # self.task = None
        logger.info("🔌 Cerrando conexión WebSocket y tareas asociadas...")

        # Cancelamos las tareas si existen
        for task_name in ["producer_task", "consumer_task"]:
            task = getattr(self, task_name, None)
            if task and not task.done():
                task.cancel()
                try:
                    await task
                    logger.info(f"🛑 {task_name} cancelada correctamente.")
                except asyncio.CancelledError:
                    logger.info(f"🛑 {task_name} fue forzada a cancelarse.")
                finally:
                    setattr(self, task_name, None)

        # Cerramos el WebSocket si está abierto
        if hasattr(self, "ws") and self.ws:
            try:
                await self.ws.close()
                logger.info("🔒 WebSocket cerrado correctamente.")
            except Exception as e:
                logger.warning(f"⚠️ Error cerrando WebSocket: {e}")
            finally:
                self.ws = None

        self.is_running = False

    # -------------------------------------------------
    def get_dataframe(self) -> pd.DataFrame:
        """Devuelve los datos como un DataFrame"""
        df = self.market_data_df.copy()
        df = df.reset_index()  # ⬅️ Asegura que 'instrument' sea una columna
        df = df.rename(columns={"index": "instrument"})  # 👈 renombrar
        if not df.empty:
            df["symbol"] = df["instrument"].str.split(" - ").str[-2]
            df["settlement"] = df["instrument"].str.split(" - ").str[-1]
        return df

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
