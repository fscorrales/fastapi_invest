from typing import List

from fastapi import APIRouter

from ...auth.services import AuthorizationDependency, OptionalAuthorizationDependency
from ...config import settings
from ..schemas import Pais, PosicionPortafolio, StoredPosicionPortafolio
from ..services import MiCuentaPortafolioServiceDependency

mi_cuenta_portafolio_router = APIRouter(
    prefix="/mi_cuenta/portafolio", tags=["IOL - Mi Cuenta"]
)


@mi_cuenta_portafolio_router.post(
    "/sync_from_iol", response_model=List[PosicionPortafolio]
)
async def sync_portafolio_from_iol(
    auth: OptionalAuthorizationDependency,
    service: MiCuentaPortafolioServiceDependency,
    username: str = None,
    password: str = None,
    pais: Pais = Pais.argentina,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.sync_portafolio_from_iol(
        username=username, password=password, pais=pais
    )


@mi_cuenta_portafolio_router.get(
    "/get_portafolio_from_db", response_model=List[StoredPosicionPortafolio]
)
async def get_portafolio_from_db(
    auth: AuthorizationDependency,
    service: MiCuentaPortafolioServiceDependency,
):
    if auth.is_admin:
        return await service.get_portafolio_from_db()
    else:
        pass
        # Si no es admin, solo devuelve las cuentas del usuario autenticado
        # (esto se maneja en el servicio)
        # Aquí podrías agregar la lógica para filtrar las cuentas del usuario autenticado
