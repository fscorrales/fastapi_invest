__all__ = ["BaseStrategy"]

import asyncio
from abc import ABC, abstractmethod
from typing import List, Union

import numpy as np
import pandas as pd

from ...config import logger
from ...primary.repositories import InstrumentsDetailsRepository
from ...primary.schemas import (
    CFICode,
    PrimaryCredentials,
    WSMarketDataSubscription,
    WSProductSubscription,
)
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA


# --------------------------------------------------
class BaseStrategy(ABC):
    # --------------------------------------------------
    def __init__(self, market_data_service: WSMarketDataService):
        self.market_data_service = market_data_service
        self._task = None
        self.is_running = False
        self.lock = asyncio.Lock()
        self.instruments_details_df = pd.DataFrame()
        self.summary_cols = []
        self.tna_requiered = None

    # --------------------------------------------------
    def get_tna_caucion(
        self,
        plazo: int,
        currency: Union[List[str], str] = ["PESOS", "DOLAR"],
    ) -> pd.DataFrame:
        if not isinstance(currency, list):
            currency = [currency]
        symbol = ["MERV - XMEV - " + c + " - " + str(plazo) + "D" for c in currency]
        ticker = currency  # ticker es igual a currency en tu formato
        df = self.market_data_service.get_dataframe()
        df = df.loc[(df["symbol"].isin(symbol)), ["symbol", "ticker", "last_price"]]
        # Asegurar que haya un registro por cada currency

        rows = []
        for s, t in zip(symbol, ticker):
            row = df[df["symbol"] == s]
            if not row.empty:
                rows.append(row.iloc[0])
            else:
                # Si no existe, agrega una fila con last_price = 0
                rows.append({"symbol": s, "ticker": t, "last_price": 0})

        df["tna_colocador"] = np.where(
            df["ticker"] == "PESOS",
            (df["last_price"] - GastosConIVA.caucion_pesos_colocador) / 100,
            (df["last_price"] - GastosConIVA.caucion_dolar_colocador) / 100,
        )
        df["tna_tomador"] = np.where(
            df["ticker"] == "PESOS",
            (df["last_price"] + GastosConIVA.caucion_pesos_tomador) / 100,
            (df["last_price"] + GastosConIVA.caucion_dolar_tomador) / 100,
        )
        return df

    # --------------------------------------------------
    async def start(self, credentials: PrimaryCredentials):
        if self._task is None or self._task.done():
            self.is_running = True
            self._task = asyncio.create_task(self._run(credentials))

    # --------------------------------------------------
    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

    # --------------------------------------------------
    async def _run(self, credentials: PrimaryCredentials):
        repo = InstrumentsDetailsRepository()
        acciones = await repo.find_by_filter(
            filters={
                "enviroment": credentials.enviroment,
                "cficode": CFICode.accion.value,
                "currency__ne": "CCL",
            }
        )

        subyacentes = await repo.find_by_filter(
            filters={
                "enviroment": credentials.enviroment,
                "cficode": CFICode.accion.value,
                "currency__ne": "CCL",
                "ticker__in": ["GGAL", "COME", "YPFD"],
                "settlement": "24hs",
            }
        )

        opciones = await repo.find_by_filter(
            filters={
                "enviroment": credentials.enviroment,
                "cficode__in": [CFICode.call_accion.value, CFICode.put_accion.value],
                "underlying__in": [
                    subyacente["underlying"] for subyacente in subyacentes
                ],
            }
        )

        cedears = await repo.find_by_filter(
            filters={
                "enviroment": credentials.enviroment,
                "cficode": CFICode.cedear.value,
                "currency__ne": "CCL",
            }
        )
        cauciones = await repo.find_by_filter(
            filters={
                "symbol": {"$regex": "-\\s[1-7]D$", "$options": "i"},
                "enviroment": credentials.enviroment,
                "cficode": CFICode.caucion.value,
            }
        )

        instruments_details = acciones + cedears + cauciones + opciones
        self.instruments_details_df = pd.DataFrame(instruments_details)

        params = WSMarketDataSubscription(
            entries=["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"],
            products=[
                WSProductSubscription(
                    symbol=i["symbol"], marketId=i["marketId"]
                ).model_dump()
                for i in instruments_details
            ],
            depth=1,
        )

        await self.market_data_service.connect(credentials, params=params)

        while self.is_running:
            try:
                async with self.market_data_service.lock:
                    df = self.market_data_service.get_dataframe()
                    if not df.empty:
                        await self.evaluate(df)
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error: {e}")

    # --------------------------------------------------
    @abstractmethod
    async def evaluate(self, df: pd.DataFrame):
        pass

    def get_dataframe(self) -> pd.DataFrame:
        return (
            self.summary_stratetgy_df.copy()
            if not self.summary_stratetgy_df.empty
            else None
        )

    def reset_dataframe(self):
        self.summary_stratetgy_df = pd.DataFrame(columns=self.summary_cols)
