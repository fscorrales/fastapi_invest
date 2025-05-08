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
    def evaluate(
        self,
        df: pd.DataFrame,
        days: int = 1,
        from_settlement: str = "CI",
        to_settlement: str = "24hs",
    ) -> pd.DataFrame:
        """ ""
        Evaluates the time arbitrage strategy between two settlements.
        It filters the DataFrame for the specified settlements and calculates the rate, TNA, and maximum quantity.
        """
        if df.empty:
            logger.warning("[TimeArbitrageStrategy] DataFrame is empty")
            return pd.DataFrame()

        try:
            # Filtramos los instrumentos que terminan en "CI" y "24hs"
            df_from = df.loc[df["settlement"] == from_settlement]
            df_to = df.loc[df["settlement"] == to_settlement]

            # Buy CI and Sell 24hs
            ## Buy CI
            df_buy = df_from.loc[:, ["symbol", "offer_size", "offer_price"]]
            df_buy["symbol_buy"] = df_buy["symbol"] + " - " + from_settlement
            ## Sell 24hs
            df_sell = df_to.loc[:, ["symbol", "bid_size", "bid_price"]]
            df_sell["symbol_sell"] = df_sell["symbol"] + " - " + to_settlement
            df_from_to = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["symbol"],
                copy=False,
            )
            df_from_to["buy_sell"] = from_settlement + " / " + to_settlement

            # Buy 24hs and Sell CI
            ## Buy 24hs
            df_buy = df_to.loc[:, ["symbol", "offer_size", "offer_price"]]
            df_buy["symbol_buy"] = df_buy["symbol"] + " - " + to_settlement
            ## Sell CI
            df_sell = df_from.loc[:, ["symbol", "bid_size", "bid_price"]]
            df_sell["symbol_sell"] = df_sell["symbol"] + " - " + from_settlement
            df_to_from = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["symbol"],
                copy=False,
            )
            df_to_from["buy_sell"] = to_settlement + " / " + from_settlement

            # Concat both DataFrames
            df = pd.concat([df_from_to.reset_index(), df_to_from.reset_index()], axis=0)
            df = df.loc[df["offer_size"] > 0]
            df = df.loc[df["bid_size"] > 0]

            # Rate
            # df["rate"] = df["adj_sell"] / df["adj_buy"] - 1
            df["rate"] = df["bid_price"] / df["offer_price"] - 1
            df["tna"] = df["rate"] / days * 365

            # Max Quantity
            df["q_max"] = df.apply(
                lambda row: min(row["offer_size"], row["bid_size"]), axis=1
            )

            # P&L
            # df["P&L"] = np.where(
            #     df["compra_venta"] == from_plazo + " / " + to_plazo,
            #     (df["adj_sell"] - df["adj_buy"])
            #     - (df["compra"] * df["tna_caucion"] / 365 * days),
            #     (df["adj_sell"] - df["adj_buy"])
            #     + (df["adj_sell"] * df["tna_caucion"] / 365 * days),
            # )
            # df["P&L"] = np.where(df["cficode"] != "ESXXXX", df["P&L"] / 100, df["P&L"])
            # df["P&L"] = df["P&L"] * df["q_max"]

            df["days"] = days
            cols = [
                "buy_sell",
                "symbol_buy",
                "symbol_sell",
                # "cficode",
                # "currency",
                # "compra",
                # "venta",
                "q_max",
                # "P&L",
                "tna",
                # "tna_operacion",
                # "tna_caucion",
                "days",
                # "var_pe",
                # "min_invest",
            ]
            df = df[cols]
            df = df.sort_values(by="tna", ascending=False)

            return df

            # for symbol in df_ci["symbol"].unique():
            #     ci_row = df_ci.loc[df_ci["symbol"] == symbol]
            #     hs24_row = df_24.loc[df_24["symbol"] == symbol]

            #     if not ci_row.empty and not hs24_row.empty:
            #         ci_price = ci_row.iloc[0].get("last_price")
            #         hs24_price = hs24_row.iloc[0].get("last_price")

            #         if ci_price and hs24_price:
            #             spread = hs24_price - ci_price
            #             logger.info(
            #                 f"[Time Arbitrage] {symbol}: 24hs={hs24_price}, CI={ci_price}, Spread={spread:.2f}"
            #             )
        except Exception as e:
            logger.error(f"[TimeArbitrageStrategy] Error en evaluación: {e}")
