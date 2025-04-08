import os

from fastapi import APIRouter

from ...auth.services import AuthorizationDependency
from ...config import IOL_PASSWORD, IOL_USERNAME, logger
from ..schemas import EstadoCuenta
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - MiCuenta"])


@mi_cuenta_router.post("/estado_cuenta", response_model=EstadoCuenta)
async def iol_estado_cuenta(
    auth: AuthorizationDependency,
    service: MiCuentaServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = os.getenv(IOL_USERNAME)
        password = os.getenv(IOL_PASSWORD)
    logger.error(f"Username: {username}, Password: {password}")

    return await service.get_mi_cuenta_estado(username=username, password=password)
