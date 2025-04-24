from typing import Annotated, List

from fastapi import APIRouter, Form, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger, settings
from ..schemas import (
    Enviroment,
    InstrumentDetails,
    ParamsInstumentDetails,
    StoredInstrumentDetails,
    FilterParamsInstrumentsDetails,
    SyncResult,
    PrimaryCredentials,
)
from ..services import InstrumentsDetailsServiceDependency

instruments_details_router = APIRouter(
    prefix="/instruments_details", tags=["Primary - Instruments Details"]
)


@instruments_details_router.post(
    "/sync_from_primary", response_model=SyncResult
)
async def sync_instruments_details_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsDetailsServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[ParamsInstumentDetails, Depends()],
):
    if auth.is_admin:
        credentials.username = (
            settings.PRIMARY_LIVE_USERNAME
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_USERNAME
        )
        credentials.password = (
            settings.PRIMARY_LIVE_PASSWORD
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_PASSWORD
        )
        credentials.url = (
            settings.PRIMARY_LIVE_URL
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_URL
        )

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    if not params.marketId or not params.symbol:
        params = None
        logger.info("No params provided")
    else:
        logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.sync_instruments_details_from_primary(
        credentials=credentials,
        params=params,
    )


@instruments_details_router.get(
    "/get_from_db", response_model=List[StoredInstrumentDetails]
)
async def get_instruments_details_from_db(
    service: InstrumentsDetailsServiceDependency,
    params: Annotated[FilterParamsInstrumentsDetails, Depends()],
):
    if params.enviroment:
        params.set_extra_filter({"enviroment": {"$eq": params.enviroment.value}})
    return await service.get_instruments_details_from_db(params=params)
