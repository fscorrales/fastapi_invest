__all__ = ["MiCuentaEstadoServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import get_estado_cuenta, get_token
from ..repositories import (
    MiCuentaCuentasRepositoryDependency,
    MiCuentaSaldosRepositoryDependency,
)
from ..schemas import Cuenta, MiCuentaEstado, SaldoCuenta


# -------------------------------------------------
@dataclass
class MiCuentaEstadoService:
    cuentas: MiCuentaCuentasRepositoryDependency
    saldos: MiCuentaSaldosRepositoryDependency

    # -------------------------------------------------
    async def sync_estado_de_cuenta_from_iol(
        self, username: str, password: str
    ) -> MiCuentaEstado:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_iol = await get_token(username, password, httpxAsyncClient=c)
                # Intentar obtener el estado de cuenta
                estado_cuenta = await get_estado_cuenta(
                    iol=connect_iol, httpxAsyncClient=c
                )

                cuentas_to_store = [
                    Cuenta(**cuenta.model_dump()) for cuenta in estado_cuenta.cuentas
                ]
                saldos_to_store = [
                    SaldoCuenta(**saldo.model_dump()) for saldo in estado_cuenta.saldos
                ]
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

    # -------------------------------------------------
    async def get_cuentas_from_db(self) -> List[Cuenta]:
        try:
            return await self.cuentas.get_all()
        except Exception as e:
            logger.error(f"Error retrieving IOL'S Cuentas from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving IOL'S Cuentas from the database",
            )

    # -------------------------------------------------
    async def get_saldos_from_db(self) -> List[SaldoCuenta]:
        try:
            return await self.saldos.get_all()
        except Exception as e:
            logger.error(f"Error retrieving IOL'S Saldos from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving IOL'S Saldos from the database",
            )


MiCuentaEstadoServiceDependency = Annotated[MiCuentaEstadoService, Depends()]
