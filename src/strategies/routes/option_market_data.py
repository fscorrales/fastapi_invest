# src/stretegies/routes/option_market_data.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...primary.schemas import (
    PrimaryCredentials,
)
from ...primary.services import (
    WSMarketDataServiceDependency,
    prepare_primary_credentials,
)
from ...utils import apply_auto_filter, safe_json_df
from ..schemas import OptionMarketDataFilter, OptionMarketDataSummary
from ..services import (
    OPTION_MARKET_DATA_NAME,
    OptionMarketDataService,
    strategy_manager,
)

STRATEGY_NAME = OPTION_MARKET_DATA_NAME

option_market_data_router = APIRouter(
    prefix="/" + STRATEGY_NAME, tags=["Strategies - Option Market Data"]
)


@option_market_data_router.post("/start", response_model=dict)
async def start_option_market_data(
    auth: OptionalAuthorizationDependency,
    service: WSMarketDataServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    days: int = 1,
    upload_to_google_sheets: bool = Query(False, alias="uploadToGoogleSheets"),
):
    if service.stream_task and not service.stream_task.done():
        raise HTTPException(status_code=400, detail="WebSocket stream already running.")

    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    if STRATEGY_NAME in strategy_manager.list_active():
        raise HTTPException(status_code=400, detail="La estrategia ya está corriendo")

    strategy = OptionMarketDataService(
        market_data_service=service,
        days=days,
        upload_to_google_sheets=upload_to_google_sheets,
    )
    strategy_manager.register(STRATEGY_NAME, strategy)
    await strategy_manager.start_strategy(STRATEGY_NAME, credentials)

    return {"message": f"Estrategia '{STRATEGY_NAME}' iniciada"}


@option_market_data_router.get("/status", response_model=dict)
async def get_strategy_status():
    is_running = STRATEGY_NAME in strategy_manager.list_active()
    return {
        "strategy": STRATEGY_NAME,
        "status": "running" if is_running else "stopped",
    }


@option_market_data_router.post("/stop")
async def stop_option_market_data():
    await strategy_manager.stop_strategy(STRATEGY_NAME)
    return {"status": "stopped", "strategy": STRATEGY_NAME}


@option_market_data_router.post("/reset", response_model=dict)
async def reset_strategy_data():
    strategy = strategy_manager.get(STRATEGY_NAME)
    if not strategy:
        raise HTTPException(status_code=404, detail="La estrategia no está activa")

    strategy.reset_dataframe()
    return {"message": "DataFrame reseteado correctamente."}


@option_market_data_router.get(
    "/dataframe", response_model=list[OptionMarketDataSummary]
)
async def get_strategy_data(
    params: Annotated[OptionMarketDataFilter, Depends()],
):
    strategy = strategy_manager.get(STRATEGY_NAME)
    if not strategy:
        raise HTTPException(status_code=404, detail="La estrategia no está activa")

    df = strategy.get_dataframe()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No hay datos disponibles")

    # Aplicar filtros
    apply_auto_filter(params)
    query = params.get_full_filter()

    # --- Aplicamos el filtro al DataFrame ---
    if query:
        for key, condition in query.items():
            if "$eq" in condition:
                df = df[df[key] == condition["$eq"]]

    # Ordenamiento
    if params.sort_by in df.columns:
        ascending = params.sort_dir == "asc"
        df = df.sort_values(by=params.sort_by, ascending=ascending)

    # Paginación
    df = df.iloc[params.offset : params.offset + params.limit]
    df = safe_json_df(df)

    return [OptionMarketDataSummary(**row.to_dict()) for _, row in df.iterrows()]
