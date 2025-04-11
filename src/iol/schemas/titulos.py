__all__ = ["FCI"]


from enum import Enum
from typing import Optional

from pydantic import BaseModel

from . import Moneda, PlazoLiquidacion


# -------------------------------------------------
class TipoFCI(str, Enum):
    plazo_fijo_pesos = "plazo_fijo_pesos"
    plazo_fijo_dolares = "plazo_fijo_dolares"
    renta_fija_pesos = "renta_fija_pesos"
    renta_fija_dolares = "renta_fija_dolares"
    renta_mixta_pesos = "renta_mixta_pesos"
    renta_mixta_dolares = "renta_mixta_dolares"
    renta_variable_pesos = "renta_variable_pesos"
    renta_variable_dolares = "renta_variable_dolares"


# -------------------------------------------------
class AdministradoraFCI(str, Enum):
    convexity = "convexity"  # En la doc IOL es "cONVEXITY"
    supervielle = "supervielle"  # En la doc IOL es "sUPERVIELLE"
    allaria = "aLLARIA"
    alliance_bernstein = "aLLIANCE_BERNSTEIN"
    dracma = "dRACMA"


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
    cedears = "cEDEARS"
    titulos_publicos = "titulosPublicos"
    acciones = "aCCIONES"
    cupones_privados = "cUPONESPRIVADOS"
    fondos_de_inversion = "fONDOSDEINVERSION"
    adr = "aDR"
    indices = "iNDICES"
    bocon = "bOCON"
    bonex = "bONEX"
    certificados_par = "cERTIFICADOSPAR"
    obligaciones_negociables = "oBLIGACIONESNEGOCIABLES"
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
    cauciones_pesos = "cAUCIONESPESOS"
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
class HorizonteInversion(str, Enum):
    corto_plazo = "corto_plazo"
    mediano_plazo = "mediano_plazo"
    largo_plazo = "largo_plazo"


# -------------------------------------------------
class FCI(BaseModel):
    variacion: Optional[float] = None
    ultimoOperado: Optional[float] = None
    horizonteInversion: Optional[HorizonteInversion] = None
    rescate: Optional[PlazoLiquidacion] = None
    invierte: Optional[str] = None
    tipoFondo: Optional[TipoFCI] = None
    avisoHorarioEjecucion: Optional[str] = None
    tipoAdministradoraTituloFCI: Optional[AdministradoraFCI] = None
    fechaCorte: Optional[str] = None
    codigoBloomberg: Optional[str] = None
    perfilInversor: Optional[str] = None
    informeMensual: Optional[str] = None
    reglamentoGestion: Optional[str] = None
    variacionMensual: Optional[float] = None
    variacionAnual: Optional[float] = None
    montoMinimo: Optional[float] = None
    simbolo: Optional[str] = None
    descripcion: Optional[str] = None
    pais: Optional[Pais] = None
    mercado: Optional[Mercado] = None
    tipo: Optional[TipoInstrumento] = None
    plazo: Optional[PlazoLiquidacion] = None
    moneda: Optional[Moneda] = None
