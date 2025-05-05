# src/strategies/services/time_arbitrage.py

import asyncio
from dataclasses import dataclass
from typing import Optional

import pandas as pd

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

            params = WSMarketDataParams(
                symbols=["GGAL"],
                settlement_terms=["CI", "24hs"],
                marketId="ROFX",
                entries=["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"],
                depth=1,
            )

            await self.market_data_service.connect(credentials, params=params)
            self._task = asyncio.create_task(self._run())

    # -------------------------------------------------
    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    # -------------------------------------------------
    async def _run(self):
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
                print(f"[TimeArbitrageStrategy] Error: {e}")

    # -------------------------------------------------
    def evaluate(self, df: pd.DataFrame):
        try:
            df_ci = df[df.index.str.endswith("CI")]
            df_24 = df[df.index.str.endswith("24hs")]

            for symbol in set(i[:-3] for i in df_ci.index):
                ci_row = df_ci.loc.get(f"{symbol}CI")
                hs24_row = df_24.loc.get(f"{symbol}24hs")

                if isinstance(ci_row, pd.Series) and isinstance(hs24_row, pd.Series):
                    ci_price = ci_row.get("last_price")
                    hs24_price = hs24_row.get("last_price")

                    if ci_price and hs24_price:
                        spread = hs24_price - ci_price
                        print(
                            f"[Time Arbitrage] {symbol}: 24hs={hs24_price}, CI={ci_price}, Spread={spread:.2f}"
                        )
        except Exception as e:
            print(f"[TimeArbitrageStrategy] Error en evaluación: {e}")
