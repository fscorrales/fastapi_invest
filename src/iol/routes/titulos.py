from typing import List

from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import settings
from ..schemas import FCI, StoredFCI
from ..services import TitulosServiceDependency

titulos_router = APIRouter(prefix="/titulos", tags=["IOL - Títulos"])


@titulos_router.post("/fci/sync_from_iol", response_model=List[FCI])
async def sync_fcis_from_iol(
    auth: OptionalAuthorizationDependency,
    service: TitulosServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.sync_fcis_from_iol(username=username, password=password)


@titulos_router.get("/fci/get_from_db", response_model=List[StoredFCI])
async def get_fcis_from_db(
    service: TitulosServiceDependency,
):
    return await service.get_fcis_from_db()
