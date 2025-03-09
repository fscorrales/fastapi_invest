__all__ = ["Cuenta", "SaldoCuenta", "EstadoCuenta"]

from enum import Enum
from typing import List

from pydantic import BaseModel, NonNegativeFloat

from ...utils import ErrorsWithDocId


class TipoCuenta(str, Enum):
    inv_arg_pesos = "inversion_Argentina_Pesos"
    inv_arg_dolares = "inversion_Argentina_Dolares"
    inv_eeuu_dolares = "inversion_Estados_Unidos_Dolares"
    adm_arg_pesos = "administrada_Argentina_Pesos"
    adm_arg_dolares = "administrada_Argentina_Dolares"
    adm_eeuu_dolares = "administrada_Estados_Unidos_Dolares"


class MonedaCuenta(str, Enum):
    peso_argentino = "peso_Argentino"
    dolar_estadounidense = "dolar_Estadounidense"
    real = "real"
    peso_mexicano = "peso_Mexicano"
    peso_chileno = "peso_Chileno"
    yen = "yen"
    libra = "libra"
    euro = "euro"
    peso_peruano = "peso_Peruano"
    peso_colombiano = "peso_Colombiano"
    peso_uruguayo = "peso_Uruguayo"


class EstadoCuenta(str, Enum):
    operable = "operable"
    cerrada = "cerrada"
    bloqueada = "bloqueada"


class Cuenta(BaseModel):
    numero: str
    tipo: TipoCuenta
    moneda: MonedaCuenta
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
    moneda: MonedaCuenta
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
