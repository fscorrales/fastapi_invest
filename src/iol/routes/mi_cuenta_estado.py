from typing import List

from fastapi import APIRouter

from ...auth.services import AuthorizationDependency, OptionalAuthorizationDependency
from ...config import settings
from ..schemas import Cuenta, MiCuentaEstado, SaldoCuenta, StoredCuentas, StoredSaldos
from ..services import MiCuentaEstadoServiceDependency

mi_cuenta_estado_router = APIRouter(
    prefix="/mi_cuenta/estado", tags=["IOL - Mi Cuenta"]
)


@mi_cuenta_estado_router.post("/sync_from_iol", response_model=MiCuentaEstado)
async def sync_estado_de_cuenta_from_iol(
    auth: OptionalAuthorizationDependency,
    service: MiCuentaEstadoServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.sync_estado_de_cuenta_from_iol(
        username=username, password=password
    )


@mi_cuenta_estado_router.get("/get_cuentas_from_db", response_model=List[StoredCuentas])
async def get_cuentas_from_db(
    auth: AuthorizationDependency,
    service: MiCuentaEstadoServiceDependency,
):
    if auth.is_admin:
        return await service.get_cuentas_from_db()
    else:
        pass
        # Si no es admin, solo devuelve las cuentas del usuario autenticado
        # (esto se maneja en el servicio)
        # Aquí podrías agregar la lógica para filtrar las cuentas del usuario autenticado


@mi_cuenta_estado_router.get("/get_saldos_from_db", response_model=List[StoredSaldos])
async def get_saldos_from_db(
    auth: AuthorizationDependency,
    service: MiCuentaEstadoServiceDependency,
):
    if auth.is_admin:
        return await service.get_saldos_from_db()
    else:
        pass
        # Si no es admin, solo devuelve los saldos del usuario autenticado
        # (esto se maneja en el servicio)
        # Aquí podrías agregar la lógica para filtrar los saldos del usuario autenticado
