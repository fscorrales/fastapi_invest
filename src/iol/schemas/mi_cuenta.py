__all__ = ["Cuenta", "SaldoCuenta", "MiCuentaEstado"]

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, NonNegativeFloat

from ...utils import ErrorsWithDocId
from . import Moneda


class TipoCuenta(str, Enum):
    inv_arg_pesos = "inversion_Argentina_Pesos"
    inv_arg_dolares = "inversion_Argentina_Dolares"
    inv_eeuu_dolares = "inversion_Estados_Unidos_Dolares"
    adm_arg_pesos = "administrada_Argentina_Pesos"
    adm_arg_dolares = "administrada_Argentina_Dolares"
    adm_eeuu_dolares = "administrada_Estados_Unidos_Dolares"


class EstadoCuenta(str, Enum):
    operable = "operable"
    cerrada = "cerrada"
    bloqueada = "bloqueada"


class Cuenta(BaseModel):
    numero: Optional[str] = None
    tipo: Optional[TipoCuenta] = None
    moneda: Optional[Moneda] = None
    disponible: Optional[NonNegativeFloat] = None
    comprometido: Optional[NonNegativeFloat] = None
    saldo: Optional[NonNegativeFloat] = None
    titulosValorizados: Optional[NonNegativeFloat] = None
    total: Optional[NonNegativeFloat] = None
    margenDescubierto: Optional[NonNegativeFloat] = None
    estado: Optional[EstadoCuenta] = None


class LiquidacionSaldo(str, Enum):
    inmediato = "inmediato"
    hrs24 = "hrs24"
    hrs48 = "hrs48"
    hrs72 = "hrs72"
    otro = "otro"
    masHrs72 = "masHrs72"


class SaldoCuenta(BaseModel):
    numero: Optional[str] = None
    tipo: Optional[TipoCuenta] = None
    moneda: Optional[Moneda] = None
    liquidacion: Optional[LiquidacionSaldo] = None
    saldo: Optional[NonNegativeFloat] = None
    comprometido: Optional[NonNegativeFloat] = None
    disponible: Optional[NonNegativeFloat] = None
    disponibleOperar: Optional[NonNegativeFloat] = None


class MiCuentaEstado(BaseModel):
    cuentas: List[Cuenta]
    saldos: List[SaldoCuenta]


class MiCuentaEstadoValidationOutput(BaseModel):
    errors: List[ErrorsWithDocId]
    validated: List[SaldoCuenta]
