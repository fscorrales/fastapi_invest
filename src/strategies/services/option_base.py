# src/strategies/services/option_base.py

__all__ = [
    "OptionBaseService",
    "OptionBaseServiceDependency",
]

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated, List, Literal, Union

import pandas as pd
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse

from ...config import logger
from ...primary.repositories import InstrumentsDetailsRepositoryDependency
from ...primary.schemas import CFICode, Enviroment
from ...utils import (
    convert_str_to_date_only_safe,
    export_dataframe_as_excel_response,
    export_multiple_dataframes_to_excel,
    stringify_complex_fields,
)


# -------------------------------------------------
@dataclass
class OptionBaseService:
    instruments_repo: InstrumentsDetailsRepositoryDependency

    # -------------------------------------------------
    async def get_options_instruments_from_db(
        self, options_underlying: Union[List[str], str] = ["GGAL"]
    ) -> pd.DataFrame:
        if isinstance(options_underlying, str):
            options_underlying = [options_underlying]

        subyacentes_docs = await self.instruments_repo.find_by_filter(
            filters={
                "enviroment": Enviroment.live.value,
                "cficode": CFICode.accion.value,
                "currency__ne": "CCL",
                "ticker__in": options_underlying,
                "settlement": "24hs",
            }
        )

        if not subyacentes_docs:
            raise HTTPException(status_code=404, detail="No se encontraron subyacentes")

        # 1. Obtener todas las opciones primero
        all_opciones_docs = await self.instruments_repo.find_by_filter(
            filters={
                "enviroment": Enviroment.live.value,
                "cficode__in": [
                    CFICode.call_accion.value,
                    CFICode.put_accion.value,
                ],
                "underlying__in": [
                    subyacente["underlying"] for subyacente in subyacentes_docs
                ],
            }
        )

        if not all_opciones_docs:
            raise HTTPException(status_code=404, detail="No se encontraron opciones")

        # 2. Agrupar maturityDate por mes/año
        maturity_groups = defaultdict(list)
        for opt in all_opciones_docs:
            try:
                maturity = datetime.strptime(str(opt["maturityDate"]), "%Y%m%d")
                key = maturity.strftime("%Y-%m")  # e.g., "2025-06"
                maturity_groups[key].append(opt)
            except Exception as e:
                logger.warning(f"Fecha inválida: {opt.get('maturityDate')} - {e}")

        # 3. Obtener los dos meses más próximos
        sorted_keys = sorted(maturity_groups.keys())
        selected_keys = sorted_keys[:2]  # primeros dos vencimientos

        # 4. Filtrar opciones
        opciones = []
        for key in selected_keys:
            opciones.extend(maturity_groups[key])

        options_df = stringify_complex_fields(pd.DataFrame(opciones))
        underlying_df = pd.DataFrame(subyacentes_docs)
        underlying_df = underlying_df.loc[:, ["ticker", "underlying"]]
        underlying_df = underlying_df.rename(
            columns={
                "ticker": "underlying_ticker",
            }
        )

        return pd.merge(
            options_df,
            underlying_df,
            how="left",
            on="underlying",
            copy=False,
        )

    # -------------------------------------------------
    async def generate_options_list(self, options_df: pd.DataFrame) -> pd.DataFrame:
        options_df = options_df.loc[
            :, ["underlying_ticker", "ticker", "cficode", "strike", "maturityDate"]
        ]
        # Rename columns
        options_df = options_df.rename(
            columns={
                "maturityDate": "expire",
                "cficode": "type",
            }
        )
        # Convert CFICODE
        options_df["type"] = options_df["type"].apply(
            lambda x: "Call" if x == CFICode.call_accion.value else "Put"
        )

        # Convert expire to date only in safe way without NaT problem
        options_df["expire"] = convert_str_to_date_only_safe(
            options_df["expire"], fmt="%Y%m%d"
        )
        # month_expire: 'mm/yyyy'
        options_df["month_expire"] = options_df["expire"].apply(
            lambda d: d.strftime("%m/%Y") if isinstance(d, date) else None
        )
        # days_expire: días hasta vencimiento
        today = date.today()
        options_df["days_expire"] = options_df["expire"].apply(
            lambda d: (d - today).days if isinstance(d, date) else 0
        )

        # Convert date to str because Google Sheets does not support date type
        # df["expire"] = df["expire"].apply(
        #     lambda d: d.strftime("%Y/%m/%d") if isinstance(d, date) else ""
        # )  # Formato YYYY-MM-DD de EEUU
        options_df["expire"] = options_df["expire"].apply(
            lambda d: d.strftime("%d/%m/%Y") if isinstance(d, date) else ""
        )  # Formato DD/MM/AAAA de Argentina
        return options_df

    # -------------------------------------------------
    async def generate_options_cross_join_spread(
        self, options_list_df: pd.DataFrame
    ) -> pd.DataFrame:
        df_x0 = options_list_df.copy()
        df_x1 = options_list_df.copy()
        df_x0 = df_x0.rename(
            columns={
                "ticker": "ticker_x0",
                "strike": "strike_x0",
            }
        )
        df_x1 = df_x1.rename(
            columns={
                "ticker": "ticker_x1",
                "strike": "strike_x1",
            }
        )
        df = pd.merge(
            left=df_x0,
            right=df_x1,
            on=[
                "underlying_ticker",
                "type",
                "expire",
                "month_expire",
                "days_expire",
            ],
            how="inner",
            copy=False,
        )
        df = df.loc[df["strike_x0"] < df["strike_x1"]]
        df = df.loc[
            :,
            [
                "underlying_ticker",
                "type",
                "expire",
                "ticker_x0",
                "ticker_x1",
                "strike_x0",
                "strike_x1",
                "month_expire",
                "days_expire",
            ],
        ]
        return df

    # -------------------------------------------------
    async def generate_options_cross_join_collar(
        self, options_list_df: pd.DataFrame
    ) -> pd.DataFrame:
        df_x0 = options_list_df.loc[options_list_df["type"] == "Put"]
        df_x1 = options_list_df.loc[options_list_df["type"] == "Call"]
        df_x0 = df_x0.rename(
            columns={
                "ticker": "ticker_x0",
                "strike": "strike_x0",
                "type": "type_x0",
            }
        )
        df_x1 = df_x1.rename(
            columns={
                "ticker": "ticker_x1",
                "strike": "strike_x1",
                "type": "type_x1",
            }
        )
        df = pd.merge(
            left=df_x0,
            right=df_x1,
            on=[
                "underlying_ticker",
                "expire",
                "month_expire",
                "days_expire",
            ],
            how="inner",
            copy=False,
        )
        df = df.loc[df["strike_x0"] <= df["strike_x1"]]
        df = df.loc[
            :,
            [
                "underlying_ticker",
                "type_x0",
                "type_x1",
                "expire",
                "ticker_x0",
                "ticker_x1",
                "strike_x0",
                "strike_x1",
                "month_expire",
                "days_expire",
            ],
        ]
        return df

    # -------------------------------------------------
    async def generate_options_cross_join_ratio(
        self, options_list_df: pd.DataFrame, ratio_type: Literal["down", "up"]
    ) -> pd.DataFrame:
        df_x0 = options_list_df.copy()
        df_x1 = options_list_df.copy()
        df_x0 = df_x0.rename(
            columns={
                "ticker": "ticker_x0",
                "strike": "strike_x0",
            }
        )
        df_x1 = df_x1.rename(
            columns={
                "ticker": "ticker_x1",
                "strike": "strike_x1",
            }
        )
        df = pd.merge(
            left=df_x0,
            right=df_x1,
            on=[
                "underlying_ticker",
                "type",
                "expire",
                "month_expire",
                "days_expire",
            ],
            how="inner",
            copy=False,
        )
        if ratio_type == "down":
            df = df.loc[df["strike_x0"] < df["strike_x1"]]
        else:
            df = df.loc[df["strike_x0"] > df["strike_x1"]]

        df = df.loc[
            :,
            [
                "underlying_ticker",
                "type",
                "expire",
                "ticker_x0",
                "ticker_x1",
                "strike_x0",
                "strike_x1",
                "month_expire",
                "days_expire",
            ],
        ]
        return df

    # -------------------------------------------------
    async def export_options_list_from_db(
        self, options_underlying: Union[List[str], str] = ["GGAL"]
    ) -> StreamingResponse:
        return export_dataframe_as_excel_response(
            await self.get_options_instruments_from_db(
                options_underlying=options_underlying
            ),
            filename="option_base.xlsx",
            sheet_name="options_list",
        )

    # -------------------------------------------------
    async def export_all_from_db(
        self,
        upload_to_google_sheets: bool = False,
    ) -> StreamingResponse:
        instrumets_df = await self.get_options_instruments_from_db()
        options_list_df = await self.generate_options_list(instrumets_df.copy())
        cross_join_spread_df = await self.generate_options_cross_join_spread(
            options_list_df.copy()
        )
        cross_join_collar_df = await self.generate_options_cross_join_collar(
            options_list_df.copy()
        )
        cross_join_ratio_down_df = await self.generate_options_cross_join_ratio(
            options_list_df.copy(), "down"
        )
        cross_join_ratio_up_df = await self.generate_options_cross_join_ratio(
            options_list_df.copy(), "up"
        )

        return export_multiple_dataframes_to_excel(
            df_sheet_pairs=[
                (instrumets_df, "options_instruments_details"),
                (options_list_df, "options_list"),
                (cross_join_spread_df, "cross_join_spread"),
                (cross_join_collar_df, "cross_join_collar"),
                (cross_join_ratio_down_df, "cross_join_ratio_down"),
                (cross_join_ratio_up_df, "cross_join_ratio_up"),
            ],
            filename="option_base.xlsx",
            spreadsheet_key="15jaKBf20jLP6mxyNVPVGFdeqsXrPy7VxbEmVmi2mfqc",
            upload_to_google_sheets=upload_to_google_sheets,
        )


OptionBaseServiceDependency = Annotated[OptionBaseService, Depends()]
