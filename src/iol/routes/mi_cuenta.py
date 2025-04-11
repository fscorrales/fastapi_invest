from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import settings
from ..schemas import MiCuentaEstado
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - MiCuenta"])


@mi_cuenta_router.post("/estado_cuenta", response_model=MiCuentaEstado)
async def iol_estado_cuenta(
    auth: OptionalAuthorizationDependency,
    service: MiCuentaServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.get_mi_cuenta_estado(username=username, password=password)
