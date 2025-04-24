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
)
from ..services import InstrumentsDetailsServiceDependency

instruments_details_router = APIRouter(
    prefix="/instruments_details", tags=["Primary - Instruments Details"]
)


@instruments_details_router.post(
    "/sync_from_primary", response_model=List[InstrumentDetails]
)
async def sync_instruments_details_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsDetailsServiceDependency,
    params: ParamsInstumentDetails = None,
    enviroment: Enviroment = Enviroment.live,
    username: str = None,
    password: str = None,
    url: str = None,
):
    if auth.is_admin:
        username = (
            settings.PRIMARY_LIVE_USERNAME
            if enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_USERNAME
        )
        password = (
            settings.PRIMARY_LIVE_PASSWORD
            if enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_PASSWORD
        )
        url = (
            settings.PRIMARY_LIVE_URL
            if enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_URL
        )

    logger.info(
        f"Syncing {enviroment.value} instruments details from Primary API with url: {url}"
    )
    if params:
        logger.info(f"Params: {params.model_dump(mode='json')}")
    else:
        logger.info("No params provided")
    instruments = await service.sync_instruments_details_from_primary(
        username=username,
        password=password,
        url=url,
        params=params,
        enviroment=enviroment.value,
    )
    return instruments[:100]


@instruments_details_router.get(
    "/get_from_db", response_model=List[StoredInstrumentDetails]
)
async def get_instruments_details_from_db(
    service: InstrumentsDetailsServiceDependency,
    params: Annotated[FilterParamsInstrumentsDetails, Depends()],
):
    if params.enviroment:
        params.set_extra_filter({"enviroment": {"$eq": params.enviroment.value}})
    return await service.get_instruments_from_db(params=params)
