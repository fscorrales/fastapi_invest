# src/routes/primary_ws_routes.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    PrimaryCredentials,
    WSMarketDataDF,
    WSMarketDataFilter,
    WSMarketDataParams,
)
from ..services import (
    WSMarketDataServiceDependency,
    prepare_primary_credentials,
)

ws_market_data_router = APIRouter(
    prefix="/ws_market_data", tags=["Primary - Websocket Market Data"]
)


@ws_market_data_router.post("/start", response_model=dict)
async def start_primary_stream(
    auth: OptionalAuthorizationDependency,
    service: WSMarketDataServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[WSMarketDataParams, Depends()],
):
    if service.task and not service.task.done():
        raise HTTPException(status_code=400, detail="WebSocket stream already running.")

    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.stream_market_data(
        credentials=credentials,
        params=params,
    )


@ws_market_data_router.post("/stop")
async def stop_primary_stream(
    service: WSMarketDataServiceDependency,
):
    await service.disconnect()
    return {"message": "WebSocket desconectado."}


@ws_market_data_router.get("/status", response_model=dict)
async def get_stream_status(
    service: WSMarketDataServiceDependency,
):
    return {"status": "running" if service.is_running else "stopped"}


@ws_market_data_router.post("/reset", response_model=dict)
async def reset_market_data(
    service: WSMarketDataServiceDependency,
):
    service.reset_dataframe()
    return {"message": "DataFrame reseteado correctamente."}


@ws_market_data_router.get("/dataframe", response_model=list[WSMarketDataDF])
async def get_market_data(
    service: WSMarketDataServiceDependency,
    params: Annotated[WSMarketDataFilter, Depends()],
):
    df = service.get_dataframe()
    if df.empty:
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

    return [WSMarketDataDF(**row.to_dict()) for _, row in df.iterrows()]
