from fastapi import APIRouter

from ..models import EstadoCuentaValidationOutput
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - MiCuenta"])


@mi_cuenta_router.get("/estado_cuenta", response_model=EstadoCuentaValidationOutput)
async def siif_download(
    ejercicio: str,
    service: MiCuentaServiceDependency,
) -> EstadoCuentaValidationOutput:
    return await service.download_and_update()
