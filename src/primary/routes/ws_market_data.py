# src/routes/primary_ws_routes.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ..schemas import (
    PrimaryCredentials,
    # RestMarketDataDocument,
    # RestMarketDataFilter,
    # SyncResult,
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
    status = "running" if service.task and not service.task.done() else "stopped"
    return {"status": status}


@ws_market_data_router.post("/reset", response_model=dict)
async def reset_market_data(
    service: WSMarketDataServiceDependency,
):
    service.data.clear()
    return {"message": "Datos de market data reseteados correctamente."}


@ws_market_data_router.get("/dataframe")
async def get_market_data(
    service: WSMarketDataServiceDependency,
):
    df = service.get_dataframe()
    return df.to_dict(orient="records")
