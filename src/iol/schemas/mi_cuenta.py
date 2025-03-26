__all__ = ["Cuenta", "SaldoCuenta", "EstadoCuenta", "EstadoCuentaValidationOutput"]

from enum import Enum
from typing import List

from pydantic import BaseModel, NonNegativeFloat

from ...utils import ErrorsWithDocId
from . Moneda


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
    numero: str
    tipo: TipoCuenta
    moneda: Moneda
    disponible: NonNegativeFloat
    comprometido: NonNegativeFloat
    saldo: NonNegativeFloat
    titulosValorizados: NonNegativeFloat
    total: NonNegativeFloat
    margenDescubierto: NonNegativeFloat
    estado: EstadoCuenta


class LiquidacionSaldo(str, Enum):
    inmediato = "inmediato"
    hrs24 = "hrs24"
    hrs48 = "hrs48"
    hrs72 = "hrs72"
    otro = "otro"
    masHrs72 = "masHrs72"


class SaldoCuenta(BaseModel):
    numero: str
    tipo: TipoCuenta
    moneda: Moneda
    liquidacion: LiquidacionSaldo
    saldo: NonNegativeFloat
    comprometido: NonNegativeFloat
    disponible: NonNegativeFloat
    disponibleOperar: NonNegativeFloat


class EstadoCuenta(BaseModel):
    cuentas: List[Cuenta]
    saldos: List[SaldoCuenta]


class EstadoCuentaValidationOutput(BaseModel):
    errors: List[ErrorsWithDocId]
    validated: List[SaldoCuenta]
