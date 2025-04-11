__all__ = ["PlazoLiquidacion", "Moneda"]

from enum import Enum


class PlazoLiquidacion(str, Enum):
    t0 = "t0"
    t1 = "t1"
    t2 = "t2"
    t3 = "t3"


class Moneda(str, Enum):
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
