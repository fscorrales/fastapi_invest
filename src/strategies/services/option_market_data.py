# src/strategies/services/option_market_data.py

__all__ = [
    "OptionMarketDataService",
    "OptionMarketDataDependency",
    "OPTION_MARKET_DATA_NAME",
]

from typing import Annotated, Type

import numpy as np
import pandas as pd
from fastapi import Depends
from pydantic import BaseModel

from ...config import logger
from ...primary.schemas import CFICode
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA, OptionMarketDataSummary
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionMarketDataService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        summary_model: Type[BaseModel] = OptionMarketDataSummary,
        days: int = 1,
        upload_to_google_sheets: bool = False,
        upload_interval: int = 10,
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.summary_cols = list(summary_model.model_fields.keys())
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)
        self._spreadsheet_key = "1ztmSxBFWo8xHYLNEJPcnHmiJf8yPohC_NKmjWar0JH4"
        self._sheet_name = "market_data"
        self._upload_interval = upload_interval
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
            logger.warning("[OptionMarketData] DataFrame is empty")
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
            df_opt = df_opt.rename(
                columns={
                    "bid_price": "bid",
                    "last_price": "last",
                    "offer_price": "ask",
                    "offer_size": "ask_size",
                    "effective_volume": "volume",
                    "nominal_volume": "nom_volumne",
                    "close_prev": "close",
                }
            )
            df_sub = df.loc[
                ((df["cficode"] == CFICode.accion.value) & (df["settlement"] == "24hs"))
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
                df["chg_pct"] = df["close"] / df["last"] - 1

                df = df[self.summary_cols]

                async with self.lock:
                    self.summary_strategy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionMarketData] Error en evaluación: {e}")


OptionMarketDataDependency = Annotated[OptionMarketDataService, Depends()]
OPTION_MARKET_DATA_NAME = "option_market_data"
