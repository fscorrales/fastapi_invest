from typing import List

from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import settings
from ..schemas import FCI
from ..services import TitulosServiceDependency

titulos_router = APIRouter(prefix="/titulos", tags=["IOL - Títulos"])


@titulos_router.post("/sync_fcis", response_model=List[FCI])
async def iol_fcis(
    auth: OptionalAuthorizationDependency,
    service: TitulosServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.sync_fcis_from_iol(username=username, password=password)
