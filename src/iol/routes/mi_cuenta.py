from fastapi import APIRouter

from ..schemas import EstadoCuenta
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - MiCuenta"])


@mi_cuenta_router.get("/estado_cuenta", response_model=EstadoCuenta)
async def iol_estado_cuenta(
    service: MiCuentaServiceDependency,
):
    return await service.get_mi_cuenta_estado()
