# src/strategies/services/option_necklace.py

__all__ = [
    "OptionNecklaceService",
    "OptionNecklaceDependency",
    "OPTION_NECKLACE_NAME",
]

from typing import Annotated, Type

import numpy as np
import pandas as pd
from fastapi import Depends
from pydantic import BaseModel

from ...config import logger
from ...primary.schemas import CFICode
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA, OptionCoberedCallSummary
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionNecklaceService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        summary_model: Type[BaseModel] = OptionCoberedCallSummary,
        days: int = 1,
        upload_to_google_sheets: bool = False,
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.summary_cols = list(summary_model.model_fields.keys())
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)
        self._spreadsheet_key = "1ztmSxBFWo8xHYLNEJPcnHmiJf8yPohC_NKmjWar0JH4"
        self._sheet_name = "necklace"
        self._upload_interval = 10  # seconds
        self.upload_to_google_sheets = upload_to_google_sheets

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
            logger.warning("[OptionNecklace] DataFrame is empty")
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
            df_opt = df.loc[(df["cficode"].isin([CFICode.call_accion.value]))]
            df_sub = df.loc[
                (
                    (df["cficode"] == CFICode.accion.value)
                    & (df["ticker"].isin(["GGAL", "COME", "YPFD"]))
                    & (df["settlement"] == "24hs")
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

            df = df.loc[df["bid_size"] > 0]

            if not df.empty:
                # Add Expire
                df = df.rename(
                    columns={
                        "maturityDate": "expire",
                    }
                )
                df["expire"] = df["expire"].astype(int)
                df["expire"] = pd.to_datetime(
                    # df["expire"],
                    # format="%Y-%m-%d %H:%M:%S.%f",
                    # errors="coerce",
                    df["expire"],
                    format="%Y%m%d",
                    errors="coerce",
                )
                # df_opt["month_expire"] = df_opt["expire"].dt.strftime("%m/%Y")
                df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
                df["days_expire"] = df["days_expire"].astype(int) + 5
                df["adj_strike"] = df["strike"] * (1 - GastosConIVA.accion)
                df["adj_close"] = df["underlying_close"] * (1 + GastosConIVA.accion)
                df["adj_prima"] = df["bid_price"] * (1 - GastosConIVA.opcion)
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
                df["protection_pct"] = df["adj_prima"] / df["adj_close"]

                df["min_invest"] = df["adj_close"] * 100
                df["vi"] = np.where(
                    df["class"] == "ITM", (df["adj_close"] - df["adj_strike"]), 0
                )
                df["ve"] = df["adj_prima"] - df["vi"]
                df["ve_pct"] = df["ve"] / df["adj_close"]

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
                df = df[self.summary_cols]

                # TNA o TNA TOTAL, qué debo usar?
                if self.tna_requiered is None:
                    df = df.loc[df["tna_total"] > df["tna_caucion"]]
                else:
                    df = df.loc[df["tna_total"] > self.tna_requiered]
                df = df.sort_values(by="tna", ascending=False)

                async with self.lock:
                    self.summary_strategy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionNecklace] Error en evaluación: {e}")


OptionNecklaceDependency = Annotated[OptionNecklaceService, Depends()]
OPTION_NECKLACE_NAME = "option_necklace_call"
