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
from ..schemas import GastosConIVA, OptionNecklaceSummary
from .base_strategy import BaseStrategy


# -------------------------------------------------
class OptionNecklaceService(BaseStrategy):
    def __init__(
        self,
        market_data_service: WSMarketDataService,
        summary_model: Type[BaseModel] = OptionNecklaceSummary,
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

    # def updateOptions(self) -> pd.DataFrame:
    #     self._TABLE_NAME = "pr_options"
    #     self._INDEX_COL = "id"
    #     self._FILTER_COL = "type"
    #     main = self.instruments.copy()
    #     # Voy probando uno a uno
    #     main = main.loc[main["cficode"].isin(["OCASPS", "OPASPS"])]
    #     # main['security_desc'] = main['security_desc'].replace({'MERV - XMEV - ': ''}, regex=True)
    #     # main[['symbol', 'time']] = main['security_desc'].str.split(pat=' - ', n=1, expand=True)
    #     main = main.loc[
    #         :,
    #         [
    #             "symbol",
    #             "time",
    #             "security_desc",
    #             "underlying",
    #             "cficode",
    #             "maturity_date",
    #             "currency",
    #             "strike",
    #         ],
    #     ]
    #     df = main
    #     df["type"] = "Call"
    #     df.loc[df["cficode"] == "OPASPS", "type"] = "Put"
    #     df = df.rename(
    #         columns={
    #             "maturity_date": "expire",
    #         }
    #     )
    #     df["month_expire"] = df["expire"].dt.strftime("%m/%Y")
    #     df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
    #     symbols = self.instruments.copy()
    #     symbols = symbols.loc[
    #         (symbols["currency"] == "ARS")
    #         & symbols["cficode"].isin(["ESXXXX", "DBXXXX", "EMXXXX"])
    #     ]
    #     symbols = symbols.loc[
    #         (
    #             (symbols["cficode"] == "ESXXXX")
    #             & (~symbols["symbol"].str.endswith("X"))
    #             | (symbols["symbol"] == "CAPX")
    #         )
    #         | (symbols["cficode"] != "ESXXXX")
    #     ]
    #     symbols = symbols.drop_duplicates(subset=(["symbol", "underlying"])).loc[
    #         :, ["symbol", "underlying"]
    #     ]
    #     symbols = symbols.rename(
    #         columns={
    #             "symbol": "symbol_underlying",
    #         }
    #     )
    #     df = df.merge(symbols, on="underlying", how="left", copy=False)
    #     df["underlying"] = df["symbol_underlying"]
    #     # print(temp)
    #     df = df.loc[
    #         :,
    #         [
    #             "underlying",
    #             "symbol",
    #             "type",
    #             "strike",
    #             "expire",
    #             "month_expire",
    #             "days_expire",
    #         ],
    #     ]
    #     # Control de registro Duplicados Options
    #     if df.duplicated(subset=["symbol"]).any():
    #         print("Registro duplicados Options (symbol) y eliminados: ")
    #         print(df.loc[df.duplicated(subset=["symbol"])])
    #         df = df.drop_duplicates(subset=["symbol"])
    #     self.df = df
    #     self.to_sql(sql_path=self.sql_path)

    # def printTibble(self):
    #     print(pydyverse.PrintTibble(self.df))

    # -------------------------------------------------
    async def evaluate(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """ """
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
            df_x0 = df.loc[(df["cficode"].isin([CFICode.put_accion.value]))]
            df_x1 = df.loc[(df["cficode"].isin([CFICode.call_accion.value]))]
            filter_cols = [
                "ticker",
                "strike",
                "cficode",
                "bid_price",
                "bid_size",
                "ask_size",
                "underlying",
                "maturityDate",
                "last_price",
            ]
            df_x0 = df_x0.rename(
                columns={
                    "ticker": "ticker_x0",
                    "strike": "strike_x0",
                    "cficode": "type_x0",
                    "bid_price": "prima_x0",
                    "ask_size": "ask_size",
                }
            )
            df_x1 = df_x1.rename(
                columns={
                    "ticker": "ticker_x1",
                    "strike": "strike_x1",
                    "cficode": "type_x1",
                    "bid_price": "prima_x1",
                    "bid_size": "bid_size",
                }
            )
            df = pd.merge(
                left=df_x0,
                right=df_x1,
                on=["underlying", "maturityDate"],
                how="inner",
                copy=False,
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
            df = pd.merge(
                left=df,
                right=df_sub,
                how="left",
                on=["underlying"],
                copy=False,
            )

            # Filter by bid_zize > 0
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

            # gtos_iva = self.getGtosConIVA()
            # df = securities_df.copy()
            # tna_caucion = self.getTNACaucion(df, days, currency=["PESOS"])
            # tna_caucion = int(tna_caucion["last"].values) / 100
            # options_join = self.options_cross_join.copy()
            # #      instrument  bid_size     bid     ask  ask_size    last  last_size  nominal_volume  effective_volume   symbol     time
            # #        <object>   <int64> <int64> <int64>   <int64> <int64>    <int64>         <int64>           <int64> <object> <object>
            # #  0  AE38C - 24hs         0       0       0         0       0          0               0                 0    AE38C     24hs
            # df_underlying = df.loc[
            #     (df["time"] == "24hs")
            #     &
            #     # (df['time'] == '48hs') &
            #     (df["symbol"].isin(self.options_details["underlying"].values.tolist())),
            #     ["symbol", "last"],
            # ].copy()
            # df_underlying = df_underlying.loc[df_underlying["last"] > 0]
            # df_underlying = df_underlying.rename(
            #     columns={"last": "underlying_close", "symbol": "underlying"}
            # )
            # df = df.loc[df["time"] == "24hs"]
            # dfx0 = df.copy()
            # dfx0 = dfx0.loc[dfx0["ask"] > 0, ["symbol", "ask", "ask_size"]]
            # dfx0 = dfx0.rename(
            #     columns={
            #         "symbol": "base_x0",
            #         "ask": "prima_x0",
            #     }
            # )
            # dfx1 = df.copy()
            # dfx1 = dfx1.loc[dfx1["bid"] > 0, ["symbol", "bid", "bid_size"]]
            # dfx1 = dfx1.rename(
            #     columns={
            #         "symbol": "base_x1",
            #         "bid": "prima_x1",
            #     }
            # )
            # options_join = self.options_cross_join.copy()
            # options_join = options_join.loc[
            #     (options_join["base_x0"].isin(dfx0["base_x0"].values.tolist()))
            #     & (options_join["base_x1"].isin(dfx1["base_x1"].values.tolist()))
            #     & (
            #         options_join["underlying"].isin(
            #             df_underlying["underlying"].values.tolist()
            #         )
            #     )
            # ]
            # options_join = pd.merge(
            #     left=options_join,
            #     right=df_underlying,
            #     on="underlying",
            #     how="left",
            #     copy=False,
            # )
            # df = pd.merge(
            #     left=options_join, right=dfx0, on="base_x0", how="left", copy=False
            # )
            # df = pd.merge(left=df, right=dfx1, on="base_x1", how="left", copy=False)
            # df["expire"] = pd.to_datetime(df["expire"], format="%Y-%m-%d %H:%M:%S.%f")
            # df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
            # df["days_expire"] = df["days_expire"].astype(int) + 1
            # df["expire"] = df["expire"].dt.strftime("%d-%m-%Y")
            # df = df.loc[df["prima_x0"] > 0]
            # df = df.loc[df["prima_x1"] > 0]

            # if len(df) > 0:
            #     df["adj_strike_x0"] = df["strike_x0"] * (1 - gtos_iva["stock"])
            #     df["adj_strike_x1"] = df["strike_x1"] * (1 - gtos_iva["stock"])
            #     df["adj_close"] = df["underlying_close"] * (1 + gtos_iva["stock"])
            #     df["adj_prima_x0"] = df["prima_x0"] * (1 + gtos_iva["option"])
            #     df["adj_prima_x1"] = df["prima_x1"] * (1 - gtos_iva["option"])
            #     df["prima_neta"] = df["adj_prima_x1"] - df["adj_prima_x0"]
            #     df["capital"] = df["adj_close"] - df["prima_neta"]

            #     df["max_profit"] = df["adj_strike_x1"] - df["capital"]
            #     df["max_profit%"] = df["max_profit"] / df["capital"]
            #     df["var_max_profit"] = df["strike_x1"] / df["underlying_close"] - 1
            #     df["tna_max_profit"] = df["max_profit%"] / df["days_expire"] * 365
            #     if self.base_strategy.tna_requerida is None:
            #         df = df.loc[df["tna_max_profit"] > tna_caucion]
            #     else:
            #         df = df.loc[df["tna_max_profit"] > self.base_strategy.tna_requerida]

            #     df["pe"] = df["capital"]
            #     df["min_invest"] = df["capital"] * 100
            #     df["var_pe"] = df["pe"] / df["underlying_close"] - 1

            #     df["max_loss"] = df["adj_strike_x0"] - df["capital"]
            #     df["var_max_loss"] = df["strike_x0"] / df["underlying_close"] - 1
            #     df["max_loss%"] = df["max_loss"] / df["capital"]
            #     df["tna_max_loss"] = df["max_loss%"] / df["days_expire"] * 365

            #     df["protection%"] = df["strike_x0"] / df["capital"]

            #     # # Función para realizar el reescalado y asignar a un nuevo campo parametrizable
            #     # def rescale(x):
            #     #     scaler = MinMaxScaler()
            #     #     cols_to_rescale = ['var_max_profit', 'var_max_loss', 'var_pe']
            #     #     for col in cols_to_rescale:
            #     #         x[f'{col}_rescaled'] = 1 / x[col]
            #     #         x[f'{col}_rescaled'] = scaler.fit_transform(x[f'{col}_rescaled'].values.reshape(-1, 1))
            #     #     return x

            #     # df = df.groupby('underlying', group_keys=True).apply(rescale)
            #     # df = df.reset_index(drop=True)

            #     # df['wt_profit'] = df['max_profit'] * df['var_max_profit_rescaled']
            #     # df['wt_loss'] = df['max_loss'] * df['var_max_loss_rescaled']
            #     # df['wt_pe'] = df['pe'] * df['var_pe_rescaled']
            #     # df['tna'] = ((df['wt_profit'] + df['wt_loss']) /
            #     #                     (df['capital']) *
            #     #                     (365 / df['days_expire']))
            #     # df['tna_adj'] = df['tna'] - ((
            #     #                     tna_caucion * (df["wt_pe"] - df["capital"])
            #     #                     ) / df['capital'])
            #     df["tna"] = 0
            #     df["tna_adj"] = 0
            #     df["tna_max_diff"] = df["tna_max_profit"] + df["tna_max_loss"]
            #     df = df[cols]
            #     # df = df.loc[df['tna_adj'] > 0]
            #     df = df.loc[
            #         df["var_max_profit"] <= 0.4
            #     ]  # Solo aquellos collares que requieran hasta un 40% de suba
            #     df = df.sort_values(by="tna_max_profit", ascending=False)
            # return df


OptionNecklaceDependency = Annotated[OptionNecklaceService, Depends()]
OPTION_NECKLACE_NAME = "option_necklace_call"
