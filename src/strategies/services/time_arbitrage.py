# src/strategies/services/time_arbitrage.py

__all__ = ["TimeArbitrageStrategyService", "TimeArbitrageStrategyDependency"]

import asyncio
from dataclasses import dataclass, field
from typing import Annotated, Optional, List, Union

import pandas as pd
from fastapi import Depends
import numpy as np

from ...config import logger
from ...primary.repositories import InstrumentsDetailsRepository
from ...primary.schemas import (
    CFICode,
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

    # --------------------------------------------------
    def get_tna_caucion(
            self, df: pd.DataFrame, plazo:int, 
            currency:Union[List[str], str] = ['PESOS', 'DOLAR']
    ) -> pd.DataFrame:
        if not isinstance(currency, list):
            currency = [currency]
        symbol = [c + " - " + str(plazo) + 'D' for c in currency]
        df = df.loc[
            (df['symbol'].isin(symbol)),
            ['symbol', 'ticker', 'last_price']
        ]
        return df

    # -------------------------------------------------
    async def _run(self, credentials: PrimaryCredentials):
        # instrument_service = InstrumentsDetailsService(
        #     instruments=InstrumentsDetailsRepository()
        # )
        # instruments = await instrument_service.get_instruments_details_from_db(
        #     params=BaseFilterParams(limit=10)
        # )
        instruments_repository = InstrumentsDetailsRepository()
        instruments_details = await instruments_repository.find_by_filter(
            filters={"enviroment": credentials.enviroment}
        )
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
        self.instruments_details_df = pd.DataFrame(instruments_details)
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
            # tna_caucion = self.get_tna_caucion(df.copy(), plazo=days, currency=['PESOS'])
            # logger.info(f"[TimeArbitrageStrategy] TNA Caución: {tna_caucion}")
            # caucion_pesos = (
            #     cauciones.loc[cauciones['symbol'] == 'PESOS', ['last']].values[0][0] -
            #     gtos_iva['caucion_pesos']
            # ) / 100
            # df['tna_caucion'] = df['currency'].apply(
            #     lambda x: caucion_pesos
            #     if x == 'ars' 
            #     else caucion_dolares
            # )
            # Add cficode and currency to WSMarketData DF and then filter with them
            df = df.merge(
                self.instruments_details_df.loc[:, ["symbol", "cficode", "currency"]],
                how="left",
                on="symbol",
            )
            # df = df.loc[df["currency"] == "ARS"] # Only ARS
            # df = df.loc[
            #     df["cficode"].isin([CFICode.accion.value, CFICode.cedear.value])
            # ]
            logger.info(
                df.loc[
                    df["ticker"].isin(["GGAL", "YPFD", "BYMA", "TXAR"]) 
                ]
            )
            # Filter by settlement
            df_from = df.loc[df["settlement"] == from_settlement]
            df_to = df.loc[df["settlement"] == to_settlement]

            # Buy CI and Sell 24hs
            ## Buy CI
            df_buy = df_from.loc[:, ["ticker", "offer_size", "offer_price", "cficode"]]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + from_settlement
            ## Sell 24hs
            df_sell = df_to.loc[:, ["ticker", "bid_size", "bid_price", "cficode"]]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + to_settlement
            df_from_to = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode"],
                copy=False,
            )
            df_from_to["buy_sell"] = from_settlement + " / " + to_settlement

            # Buy 24hs and Sell CI
            ## Buy 24hs
            df_buy = df_to.loc[:, ["ticker", "offer_size", "offer_price", "cficode"]]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + to_settlement
            ## Sell CI
            df_sell = df_from.loc[:, ["ticker", "bid_size", "bid_price", "cficode"]]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + from_settlement
            df_to_from = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode"],
                copy=False,
            )
            df_to_from["buy_sell"] = to_settlement + " / " + from_settlement

            # Concat both DataFrames
            df = pd.concat([df_from_to, df_to_from], axis=0, ignore_index=True)
            # df = df.dropna(subset=["ticker_buy", "ticker_sell"])
            df = df.loc[df["offer_size"] > 0]
            df = df.loc[df["bid_size"] > 0]

            if not df.empty:
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

                # df["cficode"] = np.select(
                #     [
                #         df["cficode"] == CFICode.accion.value,  # Stock
                #         df["cficode"] == CFICode.cedear.value,  # CEDEAR
                #         df["cficode"] == CFICode.bono.value,  # Bond
                #         df["cficode"] == CFICode.letra.value,  # Letter
                #         df["cficode"] == CFICode.on.value,  # ON
                #     ],
                #     [
                #         CFICode.accion.name, 
                #         CFICode.cedear.name,
                #         CFICode.bono.name, 
                #         CFICode.letra.name, 
                #         CFICode.on.name
                #     ],
                # )

                cficode_map = {code.value: code.name for code in CFICode}
                df["cficode"] = df["cficode"].map(cficode_map)
                df["days"] = days
                cols = [
                    "buy_sell",
                    "cficode",
                    "ticker_buy",
                    "ticker_sell",
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
                # df = df.loc[df["tna"] > 0]
                df = df.sort_values(by="tna", ascending=False)

                async with self.lock:
                    self.summary_stratetgy_df = df.copy()

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
