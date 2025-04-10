__all__ = ["MiCuentaCuentasRepository", "MiCuentaSaldosRepository"]

from .base_repository import BaseRepository
from ..schemas import Cuenta, SaldoCuenta

class MiCuentaCuentasRepository(BaseRepository[Cuenta]):
    collection_name = "iol_mi_cuenta_cuentas"
    model = Cuenta

class MiCuentaSaldosRepository(BaseRepository[SaldoCuenta]):
    collection_name = "iol_mi_cuenta_saldos"
    model = SaldoCuenta