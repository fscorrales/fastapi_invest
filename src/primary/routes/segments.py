from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    FilterParamsSegments,
    PrimaryCredentials,
    StoredSegment,
    SyncResult,
)
from ..services import SegmentsServiceDependency, prepare_primary_credentials

segments_router = APIRouter(prefix="/segments", tags=["Primary - Segments"])


@segments_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_segments_from_primary(
    auth: OptionalAuthorizationDependency,
    service: SegmentsServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} segments from Primary API with url: {credentials.url}"
    )
    return await service.sync_segments_from_primary(credentials=credentials)


@segments_router.get("/get_from_db", response_model=List[StoredSegment])
async def get_segments_from_db(
    service: SegmentsServiceDependency,
    params: Annotated[FilterParamsSegments, Depends()],
):
    apply_auto_filter(params=params)
    return await service.get_segments_from_db(params=params)
