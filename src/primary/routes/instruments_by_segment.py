from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    FilterParamsInstrumentsBySegment,
    ParamsInstumentsBySegment,
    PrimaryCredentials,
    StoredInstrumentBySegment,
    SyncResult,
)
from ..services import (
    InstrumentsBySegmentServiceDependency,
    prepare_primary_credentials,
)

instruments_by_segment_router = APIRouter(
    prefix="/instruments_by_segment", tags=["Primary - Instruments By Segment"]
)


@instruments_by_segment_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_instruments_by_segment_from_primary(
    auth: OptionalAuthorizationDependency,
    service: InstrumentsBySegmentServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[ParamsInstumentsBySegment, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.sync_instruments_by_segment_from_primary(
        credentials=credentials,
        params=params,
    )


@instruments_by_segment_router.get(
    "/get_from_db", response_model=List[StoredInstrumentBySegment]
)
async def get_instruments_by_segment_from_db(
    service: InstrumentsBySegmentServiceDependency,
    params: Annotated[FilterParamsInstrumentsBySegment, Depends()],
):
    apply_auto_filter(params=params)
    return await service.get_instruments_by_segment_from_db(params=params)
