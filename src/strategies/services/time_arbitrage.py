# src/strategies/services/time_arbitrage.py

__all__ = ["TimeArbitrageStrategyService", "TimeArbitrageStrategyDependency"]

import asyncio
from dataclasses import dataclass, field
from typing import Annotated, Optional

import pandas as pd
from fastapi import Depends

from ...config import logger
from ...primary.repositories import InstrumentsDetailsRepository
from ...primary.schemas import (
    PrimaryCredentials,
    WSMarketDataSubscription,
    WSProductSubscription,
)
from ...primary.services import WSMarketDataService


def _init_summary_strategy_df():
    df = pd.DataFrame(
        columns=[
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
    )
    return df


# -------------------------------------------------
@dataclass
class TimeArbitrageStrategyService:
    market_data_service: WSMarketDataService
    _task: Optional[asyncio.Task] = None
    is_running: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    summary_stratetgy_df: pd.DataFrame = field(
        default_factory=_init_summary_strategy_df
    )
    instruments_details_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    # -------------------------------------------------
    async def start(self, credentials: PrimaryCredentials):
        if self._task is None or self._task.done():
            self.is_running = True

            self._task = asyncio.create_task(self._run(credentials=credentials))

    # -------------------------------------------------
    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

    # -------------------------------------------------
    async def _run(self, credentials: PrimaryCredentials):
        # instrument_service = InstrumentsDetailsService(
        #     instruments=InstrumentsDetailsRepository()
        # )
        # instruments = await instrument_service.get_instruments_details_from_db(
        #     params=BaseFilterParams(limit=10)
        # )
        instruments_repository = InstrumentsDetailsRepository()
        self.instruments_details_df = await instruments_repository.find_by_filter(
            limit=10, filters={"enviroment": credentials.enviroment}
        )
        params = WSMarketDataSubscription(
            entries=["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"],
            products=[
                WSProductSubscription(
                    symbol=i["symbol"], marketId=i["marketId"]
                ).model_dump()
                for i in self.instruments_details_df
            ],
            depth=1,
        )
        # params = WSMarketDataSubscription(
        #     entries=["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"],
        #     products=[
        #         WSProductSubscription(
        #             symbol="MERV - XMEV - GGAL - CI", marketId="ROFX"
        #         ).model_dump(),
        #         WSProductSubscription(
        #             symbol="MERV - XMEV - GGAL - 24hs", marketId="ROFX"
        #         ).model_dump(),
        #     ],
        #     depth=1,
        # )
        await self.market_data_service.connect(credentials, params=params)
        logger.info("[TimeArbitrageStrategy] Conexión al WebSocket iniciada")

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
                logger.error(f"[TimeArbitrageStrategy] Error: {e}")

    # -------------------------------------------------
    async def evaluate(
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

            async with self.lock:
                self.summary_stratetgy_df = df.copy()

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

    # -------------------------------------------------
    def get_dataframe(self) -> pd.DataFrame:
        """Devuelve los datos como un DataFrame"""
        if self.summary_stratetgy_df.empty:
            # raise ValueError("El DataFrame está vacío")
            return None

        df = self.summary_stratetgy_df.copy()
        return df

    # -------------------------------------------------
    def reset_dataframe(self):
        """Limpia el DataFrame y la lista de datos acumulados"""
        self.market_data_df = _init_summary_strategy_df()


TimeArbitrageStrategyDependency = Annotated[TimeArbitrageStrategyService, Depends()]
