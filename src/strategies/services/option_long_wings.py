# src/strategies/services/option_long_wings.py

__all__ = [
    "OptionLongWingsService",
    "OptionLongWingsDependency",
    "OPTION_LONG_WINGS_NAME",
]

from typing import Annotated, Type

import numpy as np
import pandas as pd
from fastapi import Depends
from pydantic import BaseModel

from ...config import logger
from ...primary.services import WSMarketDataService
from ..schemas import OptionLongWingsSummary
from ..services import (
    OPTION_BEAR_SPREAD_NAME,
    OPTION_BULL_SPREAD_NAME,
    strategy_manager,
)
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionLongWingsService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService = None,
        summary_model: Type[BaseModel] = OptionLongWingsSummary,
        days: int = 1,
        upload_to_google_sheets: bool = False,
        upload_interval: int = 10,
        q_bull_limit: int = 20,
        q_bear_limit: int = 20,
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.summary_cols = list(summary_model.model_fields.keys())
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)
        self._spreadsheet_key = "1ztmSxBFWo8xHYLNEJPcnHmiJf8yPohC_NKmjWar0JH4"
        self._sheet_name = "long_wings"
        self._upload_interval = upload_interval
        self.upload_to_google_sheets = upload_to_google_sheets
        self.q_bull_limit = q_bull_limit
        self.q_bear_limit = q_bear_limit

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
            logger.warning("[OptionLongWings] DataFrame is empty")
            return pd.DataFrame()

        try:
            bull = strategy_manager.get(OPTION_BULL_SPREAD_NAME)
            bear = strategy_manager.get(OPTION_BEAR_SPREAD_NAME)

            if not bull or not bear:
                logger.warning(
                    "[OptionLongWings] Bull o Bear strategy no están registradas."
                )
                return

            df_bull = bull.get_dataframe()
            df_bear = bear.get_dataframe()

            if df_bull is None or df_bear is None:
                logger.warning(
                    "[OptionLongWings] Bull o Bear strategy aún no tienen datos."
                )
                return

            df_bull = df_bull.loc[
                :,
                [
                    "underlying_ticker",
                    "type",
                    "days_expire",
                    "ticker_x0",
                    "ticker_x1",
                    "strike_x0",
                    "strike_x1",
                    "prima_x0",
                    "prima_x1",
                    "underlying_close",
                    "prima_neta",
                    "spread",
                ],
            ]
            df_bull = df_bull.rename(
                columns={
                    "type": "type_bull",
                    "prima_neta": "prima_neta_bull",
                    "spread": "spread_bull",
                }
            )
            df_bear = df_bear.loc[
                :,
                [
                    "underlying_ticker",
                    "type",
                    "days_expire",
                    "ticker_x0",
                    "ticker_x1",
                    "strike_x0",
                    "strike_x1",
                    "prima_x0",
                    "prima_x1",
                    "prima_neta",
                    "spread",
                ],
            ]
            df_bear = df_bear.rename(
                columns={
                    "type": "type_bear",
                    "ticker_x0": "ticker_x2",
                    "ticker_x1": "ticker_x3",
                    "strike_x0": "strike_x2",
                    "strike_x1": "strike_x3",
                    "prima_x0": "prima_x2",
                    "prima_x1": "prima_x3",
                    "prima_neta": "prima_neta_bear",
                    "spread": "spread_bear",
                }
            )

            df = pd.merge(
                left=df_bull,
                right=df_bear,
                on=["underlying_ticker", "days_expire"],
                how="inner",
                copy=False,
            )
            df = df.loc[df["strike_x1"] <= df["strike_x2"]]

            if not df.empty:
                df["type"] = "Long "
                df["type"] = df["type"] + np.where(
                    df["type_bull"] == df["type_bear"], df["type_bull"], "Iron"
                )
                df["type"] = df["type"] + np.where(
                    df["strike_x1"] == df["strike_x2"], " Butterfly", " Condor"
                )

                # Función para calcular el MCD de dos números
                def gcd(a, b):
                    while b != 0:
                        a, b = b, a % b
                    return a

                df["gcd"] = df.apply(
                    lambda row: gcd(row["spread_bull"], row["spread_bear"]), axis=1
                )
                df["q_bull"] = df["spread_bear"] / df["gcd"]
                df["q_bear"] = df["spread_bull"] / df["gcd"]
                # Filtramos en función de la cantidad de lotes necesarios
                df = df.loc[df["q_bull"] <= self.q_bull_limit]
                df = df.loc[df["q_bear"] <= self.q_bear_limit]

                df["prima_neta"] = (
                    df["q_bull"] * df["prima_neta_bull"]
                    + df["q_bear"] * df["prima_neta_bear"]
                )

                df = df.loc[
                    (df["type"].str.contains("Iron")) & (df["prima_neta"] > 0)
                    | ~df["type"].str.contains("Iron")
                ]

                df["min_invest"] = np.where(
                    df["type"].str.contains("Iron"),
                    0,  # hay que reveer por el tema garantías
                    df["prima_neta"] * 100,
                )

                df["max_profit"] = 100 * df["prima_neta"]
                df["max_profit"] = np.where(
                    df["type"].str.contains("Iron"),
                    df["max_profit"],
                    df["max_profit"] + (df["q_bull"] * df["spread_bull"]) * 100,
                )
                df["max_loss"] = np.where(
                    df["type"].str.contains("Iron"),
                    ((df["q_bull"] * df["spread_bull"]) * 100 - df["max_profit"]) * -1,
                    (
                        df["q_bull"] * df["prima_neta_bull"]
                        + df["q_bear"] * df["prima_neta_bear"]
                    )
                    * 100,
                )

                df["pe_max_profit"] = (df["strike_x1"] + df["strike_x2"]) / 2
                df["pe_inf"] = df["strike_x1"] - df["max_profit"] / (100 * df["q_bull"])
                df["pe_sup"] = df["strike_x2"] + df["max_profit"] / (100 * df["q_bear"])
                df["spread_pe_inf_sup"] = (df["pe_sup"] - df["pe_inf"]) / df[
                    "underlying_close"
                ]

                df["var_max_profit"] = df["pe_max_profit"] / df["underlying_close"] - 1
                df["var_pe_inf"] = df["pe_inf"] / df["underlying_close"] - 1
                df["var_pe_sup"] = df["pe_sup"] / df["underlying_close"] - 1
                df["var_max_loss_inf"] = df["strike_x0"] / df["underlying_close"] - 1
                df["var_max_loss_sup"] = df["strike_x3"] / df["underlying_close"] - 1

                df["max_profit_over_max_loss"] = (
                    df["max_profit"] / (df["max_loss"] * -1) - 1
                )
                df = df.loc[
                    (
                        (df["max_profit_over_max_loss"] > 4)
                        & (df["max_profit_over_max_loss"] < 50)
                    )  # La máxima gcia debe ser el doble que la máxima pérdida
                    | (df["max_loss"] > 0)  # o la máxima perdida debe ser positiva
                ]

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
            logger.error(f"[OptionLongWings] Error en evaluación: {e}")


OptionLongWingsDependency = Annotated[OptionLongWingsService, Depends()]
OPTION_LONG_WINGS_NAME = "option_long_wings"
