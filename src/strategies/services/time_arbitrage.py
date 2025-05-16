# src/strategies/services/time_arbitrage.py

__all__ = ["TimeArbitrageStrategyService", "TimeArbitrageStrategyDependency"]

from typing import Annotated, List, Union

import pandas as pd
import numpy as np
from fastapi import Depends

from ...config import logger
from ...primary.schemas import CFICode
from .base_strategy import BaseStrategy
from ..schemas import GastosConIVA


# -------------------------------------------------
class TimeArbitrageStrategyService(BaseStrategy):
    def __init__(self, market_data_service):
        super().__init__(market_data_service=market_data_service)
        self.summary_cols = [
            "buy_sell",
            "ticker",
            "cficode",
            "ticker_buy",
            "ticker_sell",
            "currency",
            "buy_price",
            "sell_price",
            "q_max",
            # "P&L",
            "tna",
            # "tna_operacion",
            # "tna_caucion",
            "days",
            # "var_pe",
            # "min_invest",
        ]
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)

    # -------------------------------------------------
    async def evaluate(
        self,
        df: pd.DataFrame,
        days: int = 3,
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
            # Add cficode and currency to WSMarketData DF and then filter with them
            df = df.merge(
                self.instruments_details_df.loc[:, ["symbol", "cficode", "currency"]],
                how="left",
                on="symbol",
            )
            df = df.loc[df["currency"].isin(["ARS", "MEP"])]  # Only ARS and MEP
            df = df.loc[
                df["cficode"].isin([CFICode.accion.value, CFICode.cedear.value])
            ]
            # Filter by settlement
            df_from = df.loc[df["settlement"] == from_settlement]
            df_to = df.loc[df["settlement"] == to_settlement]

            # Buy CI and Sell 24hs
            ## Buy CI
            df_buy = df_from.loc[:, ["ticker", "offer_size", "offer_price", "cficode", "currency"]]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + from_settlement
            ## Sell 24hs
            df_sell = df_to.loc[:, ["ticker", "bid_size", "bid_price", "cficode", "currency"]]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + to_settlement
            df_from_to = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode", "currency"],
                copy=False,
            )
            df_from_to["buy_sell"] = from_settlement + " / " + to_settlement

            # Buy 24hs and Sell CI
            ## Buy 24hs
            df_buy = df_to.loc[:, ["ticker", "offer_size", "offer_price", "cficode", "currency"]]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + to_settlement
            ## Sell CI
            df_sell = df_from.loc[:, ["ticker", "bid_size", "bid_price", "cficode", "currency"]]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + from_settlement
            df_to_from = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode", "currency"],
                copy=False,
            )
            df_to_from["buy_sell"] = to_settlement + " / " + from_settlement

            # Concat both DataFrames
            df = pd.concat([df_from_to, df_to_from], axis=0, ignore_index=True)
            # df = df.dropna(subset=["ticker_buy", "ticker_sell"])
            df = df.loc[df["offer_size"] > 0]
            df = df.loc[df["bid_size"] > 0]

            if not df.empty:
                gastos_dict = {
                    CFICode.accion.value: GastosConIVA.accion,
                    CFICode.cedear.value: GastosConIVA.cedear,
                    CFICode.bono.value: GastosConIVA.bono,
                    CFICode.letra.value: GastosConIVA.letra,
                    CFICode.on.value: GastosConIVA.on
                }
                df['adj_buy'] = df['offer_price'] * (1 + df['cficode'].map(gastos_dict))
                df['adj_sell'] = df['bid_price'] * (1 - df['cficode'].map(gastos_dict))
                # Rate
                df["rate"] = df["adj_sell"] / df["adj_buy"] - 1
                df["tna_operacion"] = df["rate"] / days * 365
                # TNA Caución
                # tna_caucion = self.get_tna_caucion(df.copy(), plazo=days)
                # df['tna_caucion'] = df['currency'].apply(
                #     lambda x: tna_caucion.loc[tna_caucion["ticker"] == "PESOS"]["tna_colocador"].values[0][0]
                #     if x == 'ars' 
                #     else tna_caucion.loc[tna_caucion["ticker"] == "DOLAR"]["tna_colocador"].values[0][0]
                # )

                # TNA
                df['tna'] = np.where(
                    df['buy_sell'] == from_settlement + " / " + to_settlement, 
                    df['tna_operacion'], 
                    df['tna_operacion']
                    # df['tna_operacion'] + df['tna_caucion']
                )

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


                cficode_map = {code.value: code.name for code in CFICode}
                df["cficode"] = df["cficode"].map(cficode_map)
                df["days"] = days
                df = df.rename(columns={
                        'offer_price':'buy_price', 
                        'bid_price':'sell_price', 
                        })
                df = df[self.summary_cols]
                df = df.loc[df["tna"] > 0]
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

    # # -------------------------------------------------
    # def reset_dataframe(self):
    #     """Limpia el DataFrame y la lista de datos acumulados"""
    #     self.market_data_df = _init_summary_strategy_df()


TimeArbitrageStrategyDependency = Annotated[TimeArbitrageStrategyService, Depends()]
