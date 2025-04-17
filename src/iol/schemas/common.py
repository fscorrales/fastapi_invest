__all__ = [
    "LoginIOL",
    "Pais",
    "Mercado",
    "TipoInstrumento",
    "PlazoLiquidacion",
    "Moneda",
]

from enum import Enum

from pydantic import BaseModel


# -------------------------------------------------
class LoginIOL(BaseModel):
    username: str
    password: str


# -------------------------------------------------
class Pais(str, Enum):
    estados_unidos = "estados_Unidos"
    argentina = "argentina"


# -------------------------------------------------
class Mercado(str, Enum):
    bcba = "bcba"  # En la doc IOL es "bCBA"
    nyse = "nYSE"
    nasdaq = "nASDAQ"
    amex = "aMEX"
    bcs = "bCS"
    rofx = "rOFX"


# -------------------------------------------------
class TipoInstrumento(str, Enum):
    opciones = "oPCIONES"
    cedears = "CEDEARS"  # En la doc IOL es "cEDEARS"
    titulos_publicos = "titulosPublicos"
    acciones = "aCCIONES"
    cupones_privados = "cUPONESPRIVADOS"
    fondos_de_inversion = "fONDOSDEINVERSION"
    adr = "aDR"
    indices = "iNDICES"
    bocon = "bOCON"
    bonex = "bONEX"
    certificados_par = "cERTIFICADOSPAR"
    obligaciones_negociables = (
        "ObligacionesNegociables"  # En la doc IOL es "oBLIGACIONESNEGOCIABLES"
    )
    obligaciones_pyme = "oBLIGACIONESPYME"
    cupones_obligaciones = "cUPONESOBL"
    letras_deprecado = "lETRASDEPRECADO"
    letes = "lETES"
    titulos_deuda = "tITULOSDEUDA"
    cupones_extranjeros = "cUPONESEXTRANJEROS"
    cupones_tpi = "cUPONESTPI"
    bonos = "bONOS"
    divisas = "dIVISAS"
    fondos_cotizantes = "fONDOSCOTIZANTES"
    cauciones_pesos = "CAUCIONESPESOS"  # En la doc IOL es "cAUCIONESPESOS"
    cauciones_dolares = "cAUCIONESDOLARES"
    certificados_credito_fiscal = "cERTIFICADOSCREDITOFISCAL"
    cedro = "cEDRO"
    boden = "bODEN"
    fondos_renta_fija = "fONDOSRENTAFIJA"
    fideicomiso = "fideicomiso"
    renta_fija = "rENTAFIJA"
    cheque_pago_diferido = "cHEQUEPAGODIFERIDO"
    componente_dee_tf = "componenteDEEtf"
    componente_dee_tf_viejo = "componenteDEEtf_Viejo"
    futuros = "futuros"
    soja = "soja"
    maiz = "maiz"
    trigo = "trigo"
    oro = "oro"
    petroleo = "petroleo"
    fideicomiso_financiero = "fideicomisoFinanciero"
    obligaciones_negociables_dos = "obligacionesNegociables"
    letra_nota = "letraNota"
    fondo_comun_de_inversion = (
        "FondoComundeInversion"  # En la doc IOL es "fondoComunDeInversion"
    )
    titulos_publicos_suscribibles = "titulosPublicosSuscribibles"
    acciones_suscribibles = "accionesSuscribibles"
    incremento_capital = "incrementoCapital"
    letes_suscribibles = "letesSuscribibles"
    letras = "letras"
    fondos_mutuos_usa = "fondosMutuosUSA"


# -------------------------------------------------
class PlazoLiquidacion(str, Enum):
    t0 = "t0"
    t1 = "t1"
    t2 = "t2"
    t3 = "t3"


# -------------------------------------------------
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
