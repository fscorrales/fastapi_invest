__all__ = ["MiCuentaServiceDependency"]

from typing import Annotated

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import COLLECTIONS, Database, logger
from ..handlers import get_estado_cuenta, get_token
from ..schemas import MiCuentaEstado, Cuenta, SaldoCuenta
from ..repositories import MiCuentaCuentasRepositoryDependency, MiCuentaSaldosRepositoryDependency


class MiCuentaService:
    def __init__(self, cuentas: MiCuentaCuentasRepositoryDependency, saldos: MiCuentaSaldosRepositoryDependency):
        self.cuentas = cuentas
        self.saldos = saldos

    async def get_mi_cuenta_estado(self, username: str, password: str) -> MiCuentaEstado:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_iol = await get_token(username, password, httpxAsyncClient=c)
                # Intentar obtener el estado de cuenta
                estado_cuenta = await get_estado_cuenta(
                    iol=connect_iol, httpxAsyncClient=c
                )

                cuentas_to_store = [Cuenta(**cuenta.dict()) for cuenta in estado_cuenta.cuentas]
                saldos_to_store = [SaldoCuenta(**saldo.dict()) for saldo in estado_cuenta.saldos]
                await self.cuentas.delete_all()
                await self.saldos.delete_all()
                await self.cuentas.save_all(cuentas_to_store)
                await self.saldos.save_all(saldos_to_store)

                return estado_cuenta
            except ValidationError as e:
                logger.error(f"Validation Error: {e}")
                raise HTTPException(
                    status_code=400, detail="Invalid response format from IOL"
                )
            except Exception as e:
                logger.error(f"Error during report processing: {e}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials or unable to authenticate",
                )


MiCuentaServiceDependency = Annotated[MiCuentaService, Depends()]
