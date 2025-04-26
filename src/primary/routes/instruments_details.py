from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    FilterParamsInstrumentsDetails,
    ParamsInstumentDetails,
    PrimaryCredentials,
    StoredInstrumentDetails,
    SyncResult,
)
from ..services import InstrumentsDetailsServiceDependency, prepare_primary_credentials

instruments_details_router = APIRouter(
    prefix="/instruments_details", tags=["Primary - Instruments Details"]
)


@instruments_details_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_instruments_details_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsDetailsServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[ParamsInstumentDetails, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

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
    apply_auto_filter(params=params)
    return await service.get_instruments_details_from_db(params=params)
