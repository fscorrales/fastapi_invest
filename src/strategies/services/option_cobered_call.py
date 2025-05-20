# src/strategies/services/option_cobered_call.py

__all__ = ["OptionCoberedCallService", "OptionCoberedCallDependency"]

from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import Depends

from ...config import logger
from ...primary.schemas import CFICode
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionCoberedCallService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        # days: int = 1,
        # from_settlement: str = "CI",
        # to_settlement: str = "24hs",
    ):
        super().__init__(market_data_service=market_data_service)
        # self.days = days
        # self.from_settlement = from_settlement
        # self.to_settlement = to_settlement
        self.summary_cols = [
            #     "underlying",
            #     "days_expire",
            #     "symbol",
            #     "tna_total",
            #     "min_invest",
            #     "protection%",
            #     "tna",
            #     "tna_extra",
            #     "var_tna_extra",
            #     "pe",
            #     "var_pe",
            #     "ve%",
            #     "bid_size",
            #     "bid",
            #     "last",
            #     "strike",
            #     "underlying_close",
            #     "vi",
            #     "ve",
        ]
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)

    # -------------------------------------------------
    async def evaluate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """ ""
        Evaluates the time arbitrage strategy between two settlements.
        It filters the DataFrame for the specified settlements and calculates the rate, TNA, and maximum quantity.
        """
        if df.empty:
            logger.warning("[OptionCoberedCall] DataFrame is empty")
            return pd.DataFrame()

        try:
            # Add cficode and currency to WSMarketData DF and then filter with them
            df = df.merge(
                self.instruments_details_df.loc[
                    :,
                    [
                        "symbol",
                        "cficode",
                        "currency",
                        "underlying",
                        "maturityDate",
                        "strike",
                    ],
                ],
                how="left",
                on="symbol",
            )
            df = df.loc[df["currency"].isin(["ARS"])]  # Only ARS

            # Filter in two dfs
            df_opt = df.loc[
                (
                    df["cficode"].isin(
                        [CFICode.call_accion.value, CFICode.put_accion.value]
                    )
                )
            ]
            df_sub = df.loc[
                (
                    df["cficode"] == CFICode.accion.value
                    and df["ticker"].isin(["GGAL", "COME", "YPFD"])
                    and df["settlement"] == "24hs"
                )
            ]
            df_sub = df_sub.loc[:, ["ticker", "underlying", "last_price"]]
            df_sub = df_sub.rename(
                columns={
                    "last_price": "underlying_close",
                    "ticker": "underlying_ticker",
                }
            )

            # Merge both DataFrames
            df = pd.merge(
                left=df_opt,
                right=df_sub,
                how="left",
                on=["underlying"],
                copy=False,
            )

            # Add Expire
            df["maturityDate"] = pd.to_datetime(
                df["maturityDate"],
                format="%Y-%m-%d %H:%M:%S.%f",
                errors="coerce",
                # df_opt["maturityDate"], format="%Y%m%d", errors="coerce"
            )
            df = df.rename(
                columns={
                    "maturityDate": "expire",
                }
            )
            # df_opt["month_expire"] = df_opt["expire"].dt.strftime("%m/%Y")
            df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
            df["days_expire"] = df["days_expire"].astype(int) + 5
            df["expire"] = df["expire"].dt.strftime("%d-%m-%Y")
            df = df.loc[df["bid_size"] > 0]

            if not df.empty:
                df["adj_strike"] = df["strike"] * (1 - GastosConIVA.accion)
                df["adj_close"] = df["underlying_close"] * (1 + GastosConIVA.accion)
                df["adj_prima"] = df["bid"] * (1 - GastosConIVA.opcion)
                df["class"] = "OTM"
                df.loc[df["adj_close"] > df["adj_strike"], ["class"]] = "ITM"
                df["pe"] = df["adj_close"] - df["adj_prima"]
                df["var_pe"] = df["pe"] / df["underlying_close"] - 1

                df["tna"] = np.where(
                    df["class"] == "ITM",
                    ((df["adj_strike"] / df["pe"]) - 1) / df["days_expire"] * 365,
                    ((df["adj_close"] / df["pe"]) - 1) / df["days_expire"] * 365,
                )
                df["tna_extra"] = np.where(
                    df["class"] == "OTM",
                    ((df["adj_strike"] / df["adj_close"]) - 1)
                    / df["days_expire"]
                    * 365,
                    0,
                )
                df["var_tna_extra"] = np.where(
                    df["class"] == "OTM",
                    ((df["adj_strike"] / df["underlying_close"]) - 1),
                    0,
                )
                df["tna_total"] = df["tna"] + df["tna_extra"]
                df["protection%"] = df["adj_prima"] / df["adj_close"]

                df["min_invest"] = df["adj_close"] * 100
                df["vi"] = np.where(
                    df["class"] == "ITM", (df["adj_close"] - df["adj_strike"]), 0
                )
                df["ve"] = df["adj_prima"] - df["vi"]
                df["ve%"] = df["ve"] / df["adj_close"]

                df["days_expire"] = df["days_expire"].astype(int) - 4

                # TNA Caución
                tna_caucion = self.get_tna_caucion(plazo=self.days)

                def get_tna_caucion_by_currency(currency):
                    if currency == "ARS":
                        vals = tna_caucion.loc[tna_caucion["ticker"] == "PESOS"][
                            "tna_colocador"
                        ].values
                    else:
                        vals = tna_caucion.loc[tna_caucion["ticker"] == "DOLAR"][
                            "tna_colocador"
                        ].values
                    return vals[0] if len(vals) > 0 else 0

                df["tna_caucion"] = df["currency"].apply(get_tna_caucion_by_currency)

                # TNA o TNA TOTAL, qué debo usar?
                if self.base_strategy.tna_requerida is None:
                    df = df.loc[df["tna_total"] > tna_caucion]
                else:
                    df = df.loc[df["tna_total"] > self.base_strategy.tna_requerida]
                df = df.sort_values(by="tna", ascending=False)
                df = df[self.summary_cols]

                async with self.lock:
                    self.summary_stratetgy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionCoberedCall] Error en evaluación: {e}")

    # --------------------------------------------------
    # def applyStrategy(
    #         self, securities_df:pd.DataFrame, days:int
    # ):
    # #   'adj_strike', 'adj_close', 'adj_prima', 'class',
    # try:

    # df = df.loc[:,[
    #     'underlying', 'symbol', 'type', 'strike',
    #     'expire', 'month_expire', 'days_expire',
    # ]]
    #     gtos_iva = self.getGtosConIVA()
    #     df = df.loc[df["bid"] > 0]
    #     tna_caucion = self.getTNACaucion(df, days, currency=["PESOS"])
    #     tna_caucion = int(tna_caucion["last"].values) / 100

    #     if len(df) > 0:
    #         df["adj_strike"] = df["strike"] * (1 - gtos_iva["stock"])
    #         df["adj_close"] = df["underlying_close"] * (1 + gtos_iva["stock"])
    #         df["adj_prima"] = df["bid"] * (1 - gtos_iva["option"])
    #         df["class"] = "OTM"
    #         df.loc[df["adj_close"] > df["adj_strike"], ["class"]] = "ITM"
    #         df["pe"] = df["adj_close"] - df["adj_prima"]
    #         df["var_pe"] = df["pe"] / df["underlying_close"] - 1

    #         df["tna"] = np.where(
    #             df["class"] == "ITM",
    #             ((df["adj_strike"] / df["pe"]) - 1) / df["days_expire"] * 365,
    #             ((df["adj_close"] / df["pe"]) - 1) / df["days_expire"] * 365,
    #         )
    #         df["tna_extra"] = np.where(
    #             df["class"] == "OTM",
    #             ((df["adj_strike"] / df["adj_close"]) - 1)
    #             / df["days_expire"]
    #             * 365,
    #             0,
    #         )
    #         df["var_tna_extra"] = np.where(
    #             df["class"] == "OTM",
    #             ((df["adj_strike"] / df["underlying_close"]) - 1),
    #             0,
    #         )
    #         df["tna_total"] = df["tna"] + df["tna_extra"]
    #         df["protection%"] = df["adj_prima"] / df["adj_close"]

    #         df["min_invest"] = df["adj_close"] * 100
    #         df["vi"] = np.where(
    #             df["class"] == "ITM", (df["adj_close"] - df["adj_strike"]), 0
    #         )
    #         df["ve"] = df["adj_prima"] - df["vi"]
    #         df["ve%"] = df["ve"] / df["adj_close"]

    #         df["days_expire"] = df["days_expire"].astype(int) - 4

    #         df = df[cols]
    #         # TNA o TNA TOTAL, qué debo usar?
    #         if self.base_strategy.tna_requerida is None:
    #             df = df.loc[df["tna_total"] > tna_caucion]
    #         else:
    #             df = df.loc[df["tna_total"] > self.base_strategy.tna_requerida]
    #         df = df.sort_values(by="tna", ascending=False)
    #     return df
    # except Exception as e:
    #     print(f"Ocurrió un error: {e}, {type(e)}")


OptionCoberedCallDependency = Annotated[OptionCoberedCallService, Depends()]
