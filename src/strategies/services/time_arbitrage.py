# src/strategies/services/time_arbitrage.py

__all__ = ["TimeArbitrageStrategyService", "TimeArbitrageStrategyDependency"]

from typing import Annotated, List, Union

import pandas as pd
from fastapi import Depends

from ...config import logger
from ...primary.schemas import (
    CFICode,
)
from .base_strategy import BaseStrategy


# -------------------------------------------------
class TimeArbitrageStrategyService(BaseStrategy):
    def __init__(self, market_data_service):
        super().__init__(market_data_service=market_data_service)
        self.summary_strategy_df = pd.DataFrame(
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

    # --------------------------------------------------
    def get_tna_caucion(
        self,
        df: pd.DataFrame,
        plazo: int,
        currency: Union[List[str], str] = ["PESOS", "DOLAR"],
    ) -> pd.DataFrame:
        if not isinstance(currency, list):
            currency = [currency]
        symbol = [c + " - " + str(plazo) + "D" for c in currency]
        df = df.loc[(df["symbol"].isin(symbol)), ["symbol", "ticker", "last_price"]]
        return df

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
            df = df.loc[df["currency"] == "ARS"]  # Only ARS
            df = df.loc[
                df["cficode"].isin([CFICode.accion.value, CFICode.cedear.value])
            ]
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
