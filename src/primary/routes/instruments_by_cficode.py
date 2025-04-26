from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    InstrumentsByCFICodeFilter,
    InstumentsByCFICodeParams,
    PrimaryCredentials,
    StoredInstrumentByCFICode,
    SyncResult,
)
from ..services import (
    InstrumentsByCFICodeServiceDependency,
    prepare_primary_credentials,
)

instruments_by_cficode_router = APIRouter(
    prefix="/instruments_by_cficode", tags=["Primary - Instruments By CFICode"]
)


@instruments_by_cficode_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_instruments_by_cficode_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsByCFICodeServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[InstumentsByCFICodeParams, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.sync_instruments_by_cficode_from_primary(
        credentials=credentials,
        params=params,
    )


@instruments_by_cficode_router.get(
    "/get_from_db", response_model=List[StoredInstrumentByCFICode]
)
async def get_instruments_by_cficode_from_db(
    service: InstrumentsByCFICodeServiceDependency,
    params: Annotated[InstrumentsByCFICodeFilter, Depends()],
):
    apply_auto_filter(params=params)
    return await service.get_instruments_by_cficode_from_db(params=params)
