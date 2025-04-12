__all__ = ["MiCuentaCuentasRepositoryDependency", "MiCuentaSaldosRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import Cuenta, SaldoCuenta


class MiCuentaCuentasRepository(BaseRepository[Cuenta]):
    collection_name = "iol_mi_cuenta_cuentas"
    model = Cuenta


class MiCuentaSaldosRepository(BaseRepository[SaldoCuenta]):
    collection_name = "iol_mi_cuenta_saldos"
    model = SaldoCuenta


MiCuentaCuentasRepositoryDependency = Annotated[MiCuentaCuentasRepository, Depends()]
MiCuentaSaldosRepositoryDependency = Annotated[MiCuentaSaldosRepository, Depends()]
