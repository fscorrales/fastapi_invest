from typing import List

from fastapi import APIRouter

from ...auth.services import AuthorizationDependency, OptionalAuthorizationDependency
from ...config import settings
from ..schemas import Cuenta, MiCuentaEstado, SaldoCuenta
from ..services import MiCuentaServiceDependency

mi_cuenta_router = APIRouter(prefix="/mi_cuenta", tags=["IOL - Mi Cuenta"])


@mi_cuenta_router.post("/estado/sync_from_iol", response_model=MiCuentaEstado)
async def sync_estado_de_cuenta_from_iol(
    auth: OptionalAuthorizationDependency,
    service: MiCuentaServiceDependency,
    username: str = None,
    password: str = None,
):
    if auth.is_admin:
        username = settings.IOL_USERNAME
        password = settings.IOL_PASSWORD

    return await service.sync_estado_de_cuenta_from_iol(
        username=username, password=password
    )


@mi_cuenta_router.get("/estado/get_cuentas_from_db", response_model=List[Cuenta])
async def get_cuentas_from_db(
    auth: AuthorizationDependency,
    service: MiCuentaServiceDependency,
):
    if auth.is_admin:
        return await service.get_cuentas_from_db()
    else:
        pass
        # Si no es admin, solo devuelve las cuentas del usuario autenticado
        # (esto se maneja en el servicio)
        # Aquí podrías agregar la lógica para filtrar las cuentas del usuario autenticado


@mi_cuenta_router.get("/estado/get_saldos_from_db", response_model=List[SaldoCuenta])
async def get_saldos_from_db(
    auth: AuthorizationDependency,
    service: MiCuentaServiceDependency,
):
    if auth.is_admin:
        return await service.get_saldos_from_db()
    else:
        pass
        # Si no es admin, solo devuelve los saldos del usuario autenticado
        # (esto se maneja en el servicio)
        # Aquí podrías agregar la lógica para filtrar los saldos del usuario autenticado
