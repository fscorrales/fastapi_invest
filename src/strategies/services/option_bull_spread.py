# src/strategies/services/option_bull_spread.py

__all__ = [
    "OptionBullSpreadService",
    "OptionBullSpreadDependency",
    "OPTION_BULL_SPREAD_NAME",
]

from typing import Annotated, Type

import numpy as np
import pandas as pd
from fastapi import Depends
from pydantic import BaseModel

from ...config import logger
from ...primary.schemas import CFICode
from ...primary.services import WSMarketDataService
from ..schemas import GastosConIVA, OptionBullSpreadSummary
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionBullSpreadService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        summary_model: Type[BaseModel] = OptionBullSpreadSummary,
        days: int = 1,
        upload_to_google_sheets: bool = False,
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.summary_cols = list(summary_model.model_fields.keys())
        self.summary_strategy_df = pd.DataFrame(columns=self.summary_cols)
        self._spreadsheet_key = "1ztmSxBFWo8xHYLNEJPcnHmiJf8yPohC_NKmjWar0JH4"
        self._sheet_name = "bull_spread_new"
        self._upload_interval = 10  # seconds
        self.upload_to_google_sheets = upload_to_google_sheets

    # -------------------------------------------------
    async def evaluate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """ """
        if df.empty:
            logger.warning("[OptionBullSpread] DataFrame is empty")
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
            df_x0 = df.loc[
                (
                    df["cficode"].isin(
                        [CFICode.put_accion.value, CFICode.call_accion.value]
                    )
                )
            ]
            df_x1 = df.loc[
                (
                    df["cficode"].isin(
                        [CFICode.put_accion.value, CFICode.call_accion.value]
                    )
                )
            ]
            filter_cols = [
                "ticker",
                "strike",
                "cficode",
                "underlying",
                "maturityDate",
                "currency",
            ]
            df_x0 = df_x0.loc[
                df_x0["offer_size"] > 0, filter_cols + ["offer_size", "offer_price"]
            ]
            df_x0 = df_x0.rename(
                columns={
                    "ticker": "ticker_x0",
                    "strike": "strike_x0",
                    "offer_price": "prima_x0",
                    "offer_size": "size_x0",
                }
            )
            df_x1 = df_x1.loc[
                df_x1["bid_size"] > 0, filter_cols + ["bid_size", "bid_price"]
            ]
            df_x1 = df_x1.rename(
                columns={
                    "ticker": "ticker_x1",
                    "strike": "strike_x1",
                    "bid_price": "prima_x1",
                    "bid_size": "size_x1",
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

                df["adj_strike_x0"] = df["strike_x0"] * (1 + GastosConIVA.accion)
                df["adj_strike_x1"] = df["strike_x1"] * (1 - GastosConIVA.accion)
                df["adj_close"] = df["underlying_close"] * (1 + GastosConIVA.accion)
                df["adj_prima_x0"] = df["prima_x0"] * (1 + GastosConIVA.opcion)
                df["adj_prima_x1"] = df["prima_x1"] * (1 - GastosConIVA.opcion)
                df["prima_neta"] = df["adj_prima_x1"] - df["adj_prima_x0"]
                df = df.loc[
                    ((df["type"] == CFICode.put_accion.name) & (df["prima_neta"] > 0))
                    | (df["type"] == CFICode.call_accion.name)
                ]
                df["spread"] = df["strike_x1"] - df["strike_x0"]
                df["spread%"] = (df["prima_neta"] * -1) / df["spread"]
                df = df.loc[
                    df["spread%"] < 0.7
                ]  # SE PUEDE REDUCIR EL ANÁLSIS A TODOS LOS QUE TENGAN MENOR SPREAD POR CADA base_x1

                df["capital"] = np.where(
                    df["type"] == CFICode.call_accion.name,
                    (df["prima_neta"] * -1),
                    df["adj_prima_x1"]
                    * 1.5,  # Es un supuesto maximizador, en realidad no sé cómo calculan
                )
                df["min_invest"] = df["capital"] * 100

                df["max_profit"] = (
                    np.where(
                        df["type"] == CFICode.call_accion.name,
                        (df["spread"] * 0.8)
                        + df["prima_neta"],  # Es dificil obtener el 100% del SPREAD
                        df["prima_neta"],
                    )
                    * 100
                )
                df["max_profit_pct"] = df["max_profit"] / df["min_invest"]
                df["var_max_profit"] = df["strike_x1"] / df["underlying_close"] - 1
                df["tna_max_profit"] = df["max_profit_pct"] / df["days_expire"] * 365

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

                if self.tna_requiered is None:
                    df = df.loc[df["tna_max_profit"] > df["tna_caucion"]]
                else:
                    df = df.loc[df["tna_max_profit"] > self.tna_requiered]

                df["pe"] = np.where(
                    df["type"] == CFICode.call_accion.name,
                    df["adj_strike_x0"] - df["prima_neta"],
                    df["adj_strike_x1"] - df["prima_neta"],
                )
                df["var_pe"] = df["pe"] / df["underlying_close"] - 1
                df["max_loss"] = (
                    np.where(
                        df["type"] == CFICode.call_accion.name,
                        df["prima_neta"],
                        (df["spread"] - df["prima_neta"]) * -1,
                    )
                    * 100
                )

                df["var_max_loss"] = df["strike_x0"] / df["underlying_close"] - 1
                df["max_loss_pct"] = df["max_loss"] / df["min_invest"]
                df["tna_max_loss"] = df["max_loss_pct"] / df["days_expire"] * 365

                # # Función para realizar el reescalado y asignar a un nuevo campo parametrizable
                # def rescale(x):
                #     scaler = MinMaxScaler()
                #     cols_to_rescale = ['var_max_profit', 'var_max_loss', 'var_pe']
                #     for col in cols_to_rescale:
                #         x[f'{col}_rescaled'] = 1 / x[col]
                #         x[f'{col}_rescaled'] = scaler.fit_transform(x[f'{col}_rescaled'].values.reshape(-1, 1))
                #     return x

                # df = df.groupby('underlying', group_keys=True).apply(rescale)
                # df = df.reset_index(drop=True)

                # df['wt_profit'] = df['max_profit'] * df['var_max_profit_rescaled']
                # df['wt_loss'] = df['max_loss'] * df['var_max_loss_rescaled']
                # df['wt_pe'] = df['pe'] * df['var_pe_rescaled']
                # df['tna'] = ((df['wt_profit'] + df['wt_loss']) /
                #                     (df['capital']) *
                #                     (365 / df['days_expire']))
                # df['tna_adj'] = df['tna'] - ((
                #                     tna_caucion * (df["wt_pe"] - df["capital"])
                #                     ) / df['capital'])

                df["tna"] = 0
                df["tna_adj"] = 0
                df["tna_max_diff"] = df["tna_max_profit"] + df["tna_max_loss"]
                df = df[self.summary_cols]
                df = df.loc[
                    df["var_max_profit"] <= 0.4
                ]  # Solo aquellas bulls que requieran hasta un 40% de suba
                df = df.sort_values(by="tna_max_profit", ascending=False)

                async with self.lock:
                    self.summary_strategy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionBullSpread] Error en evaluación: {e}")


OptionBullSpreadDependency = Annotated[OptionBullSpreadService, Depends()]
OPTION_BULL_SPREAD_NAME = "option_bull_spread"
