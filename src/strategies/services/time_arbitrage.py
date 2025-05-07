# src/strategies/services/time_arbitrage.py

import asyncio
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from ...config import logger
from ...primary.schemas import PrimaryCredentials, WSMarketDataParams
from ...primary.services import WSMarketDataService


# -------------------------------------------------
@dataclass
class TimeArbitrageStrategy:
    market_data_service: WSMarketDataService
    _task: Optional[asyncio.Task] = None
    _running: bool = False

    # -------------------------------------------------
    async def start(self, credentials: PrimaryCredentials):
        if self._task is None or self._task.done():
            self._running = True

            self._task = asyncio.create_task(self._run(credentials=credentials))

    # -------------------------------------------------
    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    # -------------------------------------------------
    async def _run(self, credentials: PrimaryCredentials):
        params = WSMarketDataParams(
            symbols=["GGAL"],
            settlement_terms=["CI", "24hs"],
            marketId="ROFX",
            entries=["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"],
            depth=1,
        )
        await self.market_data_service.connect(credentials, params=params)
        logger.info("[TimeArbitrageStrategy] Conexión al WebSocket iniciada")

        while self._running:
            try:
                async with self.market_data_service.lock:
                    df = self.market_data_service.get_dataframe()
                    if not df.empty:
                        self.evaluate(df)
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TimeArbitrageStrategy] Error: {e}")

    # -------------------------------------------------
    def evaluate(self, df: pd.DataFrame):
        try:
            # Filtramos los instrumentos que terminan en "CI" y "24hs"
            df_ci = df.loc[df["settlement"] == "CI"]
            df_24 = df.loc[df["settlement"] == "24hs"]

            for symbol in df_ci["symbol"].unique():
                ci_row = df_ci.loc[df_ci["symbol"] == symbol]
                hs24_row = df_24.loc[df_24["symbol"] == symbol]

                if not ci_row.empty and not hs24_row.empty:
                    ci_price = ci_row.iloc[0].get("last_price")
                    hs24_price = hs24_row.iloc[0].get("last_price")

                    if ci_price and hs24_price:
                        spread = hs24_price - ci_price
                        logger.info(
                            f"[Time Arbitrage] {symbol}: 24hs={hs24_price}, CI={ci_price}, Spread={spread:.2f}"
                        )
        except Exception as e:
            logger.error(f"[TimeArbitrageStrategy] Error en evaluación: {e}")
