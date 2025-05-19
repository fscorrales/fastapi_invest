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
        days: int = 1,
        from_settlement: str = "CI",
        to_settlement: str = "24hs",
    ):
        super().__init__(market_data_service=market_data_service)
        self.days = days
        self.from_settlement = from_settlement
        self.to_settlement = to_settlement
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
            "p_and_l",
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
                self.instruments_details_df.loc[:, ["symbol", "cficode", "currency"]],
                how="left",
                on="symbol",
            )
            df = df.loc[df["currency"].isin(["ARS", "MEP"])]  # Only ARS and MEP
            df = df.loc[
                df["cficode"].isin([CFICode.accion.value, CFICode.cedear.value])
            ]
            # Filter by settlement
            df_from = df.loc[df["settlement"] == self.from_settlement]
            df_to = df.loc[df["settlement"] == self.to_settlement]

            # Buy CI and Sell 24hs
            ## Buy CI
            df_buy = df_from.loc[
                :, ["ticker", "offer_size", "offer_price", "cficode", "currency"]
            ]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + self.from_settlement
            ## Sell 24hs
            df_sell = df_to.loc[
                :, ["ticker", "bid_size", "bid_price", "cficode", "currency"]
            ]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + self.to_settlement
            df_from_to = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode", "currency"],
                copy=False,
            )
            df_from_to["buy_sell"] = self.from_settlement + " / " + self.to_settlement

            # Buy 24hs and Sell CI
            ## Buy 24hs
            df_buy = df_to.loc[
                :, ["ticker", "offer_size", "offer_price", "cficode", "currency"]
            ]
            df_buy["ticker_buy"] = df_buy["ticker"] + " - " + self.to_settlement
            ## Sell CI
            df_sell = df_from.loc[
                :, ["ticker", "bid_size", "bid_price", "cficode", "currency"]
            ]
            df_sell["ticker_sell"] = df_sell["ticker"] + " - " + self.from_settlement
            df_to_from = pd.merge(
                left=df_buy,
                right=df_sell,
                how="outer",
                on=["ticker", "cficode", "currency"],
                copy=False,
            )
            df_to_from["buy_sell"] = self.to_settlement + " / " + self.from_settlement

            # Concat both DataFrames
            df = pd.concat([df_from_to, df_to_from], axis=0, ignore_index=True)
            # df = df.dropna(subset=["ticker_buy", "ticker_sell"])
            df = df.loc[df["offer_size"] > 0]
            df = df.loc[df["bid_size"] > 0]

            if not df.empty:
                # Renema offer_price and bid_price
                df = df.rename(
                    columns={
                        "offer_price": "buy_price",
                        "bid_price": "sell_price",
                    }
                )
                gastos_dict = {
                    CFICode.accion.value: GastosConIVA.accion,
                    CFICode.cedear.value: GastosConIVA.cedear,
                    CFICode.bono.value: GastosConIVA.bono,
                    CFICode.letra.value: GastosConIVA.letra,
                    CFICode.on.value: GastosConIVA.on,
                }
                df["adj_buy"] = df["buy_price"] * (1 + df["cficode"].map(gastos_dict))
                df["adj_sell"] = df["sell_price"] * (1 - df["cficode"].map(gastos_dict))

                # Rate
                df["rate"] = df["adj_sell"] / df["adj_buy"] - 1
                df["tna_operacion"] = df["rate"] / self.days * 365

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

                # TNA
                df["tna"] = np.where(
                    df["buy_sell"] == self.from_settlement + " / " + self.to_settlement,
                    df["tna_operacion"],
                    df["tna_operacion"] + df["tna_caucion"],
                )

                # Max Quantity
                df["q_max"] = df.apply(
                    lambda row: min(row["offer_size"], row["bid_size"]), axis=1
                )

                # Rename cficode
                cficode_map = {code.value: code.name for code in CFICode}
                df["cficode"] = df["cficode"].map(cficode_map)

                # P&L
                df["p_and_l"] = np.where(
                    df["buy_sell"] == self.from_settlement + " / " + self.to_settlement,
                    (df["adj_sell"] - df["adj_buy"])
                    - (df["buy_price"] * df["tna_caucion"] / 365 * self.days),
                    (df["adj_sell"] - df["adj_buy"])
                    + (df["adj_sell"] * df["tna_caucion"] / 365 * self.days),
                )
                df["p_and_l"] = np.where(
                    df["cficode"] != CFICode.accion.name,
                    df["p_and_l"] / 100,
                    df["p_and_l"],
                )
                df["p_and_l"] = df["p_and_l"] * df["q_max"]

                df["days"] = self.days

                df = df[self.summary_cols]
                df = df.loc[df["tna"] > 0]
                df = df.sort_values(by="tna", ascending=False)

                async with self.lock:
                    self.summary_stratetgy_df = df.copy()

        except Exception as e:
            logger.error(f"[OptionCoberedCall] Error en evaluación: {e}")

    # --------------------------------------------------
    # def applyStrategy(
    #         self, securities_df:pd.DataFrame, days:int
    # ):
    # cols = [
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
    # ]
    # #   'adj_strike', 'adj_close', 'adj_prima', 'class',
    # try:
    #     gtos_iva = self.getGtosConIVA()
    #     df = securities_df.copy()
    #     df = df.loc[df["bid"] > 0]
    #     tna_caucion = self.getTNACaucion(df, days, currency=["PESOS"])
    #     tna_caucion = int(tna_caucion["last"].values) / 100
    #     options_details = self.options_details.copy()
    #     options_details = options_details.loc[
    #         (options_details["symbol"].isin(df["symbol"].values.tolist()))
    #         & (options_details["type"] == "Call")
    #     ]
    #     df_underlying = df.loc[
    #         (df["time"] == "24hs")
    #         &
    #         # (df['time'] == '48hs') &
    #         (df["symbol"].isin(options_details["underlying"].values.tolist())),
    #         ["symbol", "last"],
    #     ].copy()
    #     df_underlying = df_underlying.rename(
    #         columns={"last": "underlying_close", "symbol": "underlying"}
    #     )
    #     df_underlying = pd.merge(
    #         left=df_underlying,
    #         right=options_details,
    #         on="underlying",
    #         how="left",
    #         copy=False,
    #     )
    #     df = df.loc[df["time"] == "24hs"]
    #     df = pd.merge(
    #         left=df_underlying, right=df, on="symbol", how="left", copy=False
    #     )
    #     df["expire"] = pd.to_datetime(df["expire"], format="%Y-%m-%d %H:%M:%S.%f")
    #     df["days_expire"] = (df["expire"] - pd.Timestamp.now()).dt.days
    #     df["days_expire"] = df["days_expire"].astype(int) + 5
    #     df["expire"] = df["expire"].dt.strftime("%d-%m-%Y")
    #     df = df.loc[df["bid"] > 0]

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
