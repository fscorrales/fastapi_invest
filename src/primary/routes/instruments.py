from typing import List

from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger, settings
from ..schemas import Enviroment, Instrument, StoredInstrument, FilterParamsInstruments
from ..services import InstrumentsServiceDependency

instruments_router = APIRouter(prefix="/instruments", tags=["Primary - Instruments"])


@instruments_router.post("/sync_from_primary", response_model=List[Instrument])
async def sync_instruments_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsServiceDependency,
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

    logger.info(f"Syncing {enviroment.value} segments from Primary API with url: {url}")
    return await service.sync_instruments_from_primary(
        username=username, password=password, url=url, enviroment=enviroment.value
    )


@instruments_router.get("/get_from_db", response_model=List[StoredInstrument])
async def get_instruments_from_db(
    service: InstrumentsServiceDependency,
    params: Annotated[FilterParamsInstruments, Depends()],
):
    # if params.enviroment:
    #     params.set_extra_filter({"enviroment": {"$eq": params.enviroment.value}})
    return await service.get_instruments_from_db(params=params)
