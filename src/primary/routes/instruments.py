from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ..schemas import (
    FilterParamsInstruments,
    PrimaryCredentials,
    StoredInstrument,
    SyncResult,
)
from ..services import InstrumentsServiceDependency, prepare_primary_credentials

instruments_router = APIRouter(prefix="/instruments", tags=["Primary - Instruments"])


@instruments_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_instruments_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )
    return await service.sync_instruments_from_primary(credentials=credentials)


@instruments_router.get("/get_from_db", response_model=List[StoredInstrument])
async def get_instruments_from_db(
    service: InstrumentsServiceDependency,
    params: Annotated[FilterParamsInstruments, Depends()],
):
    if params.enviroment:
        params.set_extra_filter({"enviroment": {"$eq": params.enviroment.value}})
    return await service.get_instruments_from_db(params=params)
