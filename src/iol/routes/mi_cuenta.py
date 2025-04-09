from fastapi import APIRouter

from ...auth.services import OptionalAuthorizationDependency
from ...config import IOL_PASSWORD, IOL_USERNAME
from ..schemas import EstadoCuenta
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - MiCuenta"])


@mi_cuenta_router.post("/estado_cuenta", response_model=EstadoCuenta)
async def iol_estado_cuenta(
    auth: OptionalAuthorizationDependency,
    service: MiCuentaServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = IOL_USERNAME
        password = IOL_PASSWORD
    print(f"username: {username}, password: {password}")

    return await service.get_mi_cuenta_estado(username=username, password=password)
