from typing import List

from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import settings, logger
from ..schemas import Segment, StoredSegment, Enviroment
from ..services import SegmentsServiceDependency

segments_router = APIRouter(prefix="/segments", tags=["Primary - Segments"])


@segments_router.post("/sync_from_primary", response_model=List[Segment])
async def sync_segments_from_primary(
    auth: OptionalAuthorizationDependency,
    service: SegmentsServiceDependency,
    enviroment: Enviroment = Enviroment.live,
    username: str = None,
    password: str = None,
    url: str = None
):
    if auth.is_admin:
        username = settings.PRIMARY_LIVE_USERNAME if enviroment == Enviroment.live else settings.PRIMARY_REMARKETS_USERNAME
        password = settings.PRIMARY_LIVE_PASSWORD if enviroment == Enviroment.live else settings.PRIMARY_REMARKETS_PASSWORD
        url = settings.PRIMARY_LIVE_URL if enviroment == Enviroment.live else settings.PRIMARY_REMARKETS_URL

    logger.info(f"Syncing {enviroment.value} segments from Primary API with url: {url}")
    return await service.sync_segments_from_primary(username=username, password=password, url=url, enviroment=enviroment.value)


@segments_router.get("/get_from_db", response_model=List[StoredSegment])
async def get_segments_from_db(
    service: SegmentsServiceDependency,
):
    return await service.get_segments_from_db()
