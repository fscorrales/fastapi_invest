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
    # ws_manager: PrimaryWebSocketManager = Depends(get_primary_ws_manager),
):
    if service.task and not service.task.done():
        raise HTTPException(status_code=400, detail="WebSocket stream already running.")

    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.sync_ws_market_data_from_primary(
        credentials=credentials,
        params=params,
    )

    # await ws_manager.connect(primary=connect_primary, msg_subscription=msg_subscription)
    # return {"message": "WebSocket conectado."}


@ws_market_data_router.post("/stop")
async def stop_primary_stream(
    # ws_manager: PrimaryWebSocketManager = Depends(get_primary_ws_manager),
    service: WSMarketDataServiceDependency,
):
    await service.disconnect()
    return {"message": "WebSocket desconectado."}


@ws_market_data_router.get("/dataframe")
async def get_market_data(
    # ws_manager: PrimaryWebSocketManager = Depends(get_primary_ws_manager),
    service: WSMarketDataServiceDependency,
):
    df = service.get_dataframe()
    return df.to_dict(orient="records")
