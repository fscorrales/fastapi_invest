# src/strategies/services/option_bear_spread.py

__all__ = [
    "OptionCallRatioBackspreadService",
    "OptionCallRatioBackspreadDependency",
    "OPTION_CALL_RATIO_BACKSPREAD_NAME",
]

from fractions import Fraction
from typing import Annotated, Type

import numpy as np
import pandas as pd
from fastapi import Depends
from pydantic import BaseModel

from ...config import logger
from ...primary.schemas import CFICode
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA, OptionRatioBackspreadSummary
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionCallRatioBackspreadService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        summary_model: Type[BaseModel] = OptionRatioBackspreadSummary,
        days: int = 1,
        upload_to_google_sheets: bool = False,
        upload_interval: int = 10,
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.summary_cols = list(summary_model.model_fields.keys())
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)
        self._spreadsheet_key = "1ztmSxBFWo8xHYLNEJPcnHmiJf8yPohC_NKmjWar0JH4"
        self._sheet_name = "ri_call"
        self._upload_interval = upload_interval
        self.upload_to_google_sheets = upload_to_google_sheets

    # -------------------------------------------------
    async def evaluate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """ """
        if df.empty:
            logger.warning("[OptionCallRatioBackspread] DataFrame is empty")
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

            # Get underlying df
            df_und = df.loc[
                ((df["cficode"] == CFICode.accion.value) & (df["settlement"] == "24hs"))
            ]
            df_und = df_und.loc[:, ["ticker", "underlying", "last_price"]]
            df_und = df_und.rename(
                columns={
                    "last_price": "underlying_close",
                    "ticker": "underlying_ticker",
                }
            )

            # Get two options DataFrames, one for puts and one for calls
            df_x0 = df.loc[(df["cficode"].isin([CFICode.call_accion.value]))]
            df_x1 = df.loc[(df["cficode"].isin([CFICode.call_accion.value]))]
            filter_cols = [
                "ticker",
                "strike",
                "cficode",
                "underlying",
                "maturityDate",
                "currency",
            ]
            df_x0 = df_x0.loc[
                df_x0["bid_size"] > 0, filter_cols + ["bid_size", "bid_price"]
            ]
            df_x0 = df_x0.rename(
                columns={
                    "ticker": "ticker_x0",
                    "strike": "strike_x0",
                    "bid_price": "prima_x0",
                    "bid_size": "size_x0",
                }
            )
            df_x1 = df_x1.loc[
                df_x1["offer_size"] > 0, filter_cols + ["offer_size", "offer_price"]
            ]
            df_x1 = df_x1.rename(
                columns={
                    "ticker": "ticker_x1",
                    "strike": "strike_x1",
                    "offer_price": "prima_x1",
                    "offer_size": "size_x1",
                }
            )
            df = pd.merge(
                left=df_x0,
                right=df_x1,
                on=["underlying", "cficode", "maturityDate", "currency"],
                how="inner",
                copy=False,
            )
            df = df.loc[df["strike_x0"] < df["strike_x1"]]

            # Merge with underlying df
            df = pd.merge(
                left=df,
                right=df_und,
                how="left",
                on=["underlying"],
                copy=False,
            )

            if not df.empty:
                # Add Expire
                df = df.rename(
                    columns={
                        "maturityDate": "expire",
                    }
                )
                df["expire"] = df["expire"].astype(int)
                df["expire"] = pd.to_datetime(
                    df["expire"],
                    format="%Y%m%d",
                    errors="coerce",
                )
                # df_opt["month_expire"] = df_opt["expire"].dt.strftime("%m/%Y")
                df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
                df["days_expire"] = df["days_expire"].astype(int) + 1

                # Rename cficode
                cficode_map = {code.value: code.name for code in CFICode}
                df["cficode"] = df["cficode"].map(cficode_map)
                df = df.rename(columns={"cficode": "type"})

                df["adj_strike_x0"] = df["strike_x0"] * (1 - GastosConIVA.accion)
                df["adj_strike_x1"] = df["strike_x1"] * (1 + GastosConIVA.accion)
                df["adj_close"] = df["underlying_close"] * (1 + GastosConIVA.accion)
                df["adj_prima_x0"] = df["prima_x0"] * (1 - GastosConIVA.opcion)
                df["adj_prima_x1"] = df["prima_x1"] * (1 + GastosConIVA.opcion)

                df["prime_relation"] = df["adj_prima_x0"] / df["adj_prima_x1"]
                df = df.loc[df["prime_relation"] > 1]
                df["q_venta"] = df["prime_relation"].apply(
                    lambda x: Fraction(x).limit_denominator(10).denominator
                )
                df["q_compra"] = df["q_venta"] + 1
                df["prima_neta"] = (df["adj_prima_x0"] * df["q_venta"]) - (
                    df["adj_prima_x1"] * df["q_compra"]
                )
                df["min_invest"] = np.where(
                    df["prima_neta"] > 0,
                    df["adj_prima_x0"]
                    * df["q_venta"]
                    * 1.5
                    * 100,  # Es un supuesto maximizador, en realidad no sé cómo calculan
                    df["prima_neta"] * -100,
                )
                df["spread"] = df["strike_x1"] - df["strike_x0"]
                df["pe_inf"] = df["strike_x0"] + (df["prima_neta"] / df["q_compra"])
                df["var_pe_inf"] = df["pe_inf"] / df["underlying_close"] - 1
                df["pe_sup"] = (
                    df["strike_x1"]
                    + (df["spread"] * df["q_venta"]) / (df["q_compra"] - df["q_venta"])
                    - df["prima_neta"]
                )
                df["var_pe_sup"] = df["pe_sup"] / df["underlying_close"] - 1
                df["spread_pe_sup_inf"] = (df["pe_sup"] - df["pe_inf"]) / df[
                    "underlying_close"
                ]
                df["max_loss"] = (df["spread"] * df["q_venta"] - df["prima_neta"]) * 100
                df["max_loss_pct"] = df["max_loss"] / df["min_invest"]
                df["pe_max_loss"] = (df["max_loss"] / 100 * -1) + df["pe_sup"]
                df["var_pe_max_loss"] = df["pe_max_loss"] / df["underlying_close"] - 1

                df = df[self.summary_cols]
                df = df.loc[df["spread_pe_sup_inf"] < 0.4]
                df = df.sort_values(by="var_pe_sup", ascending=False)

                async with self.lock:
                    self.summary_strategy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionCallRatioBackspread] Error en evaluación: {e}")


OptionCallRatioBackspreadDependency = Annotated[
    OptionCallRatioBackspreadService, Depends()
]
OPTION_CALL_RATIO_BACKSPREAD_NAME = "option_call_ratio_backspread"
