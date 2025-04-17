__all__ = ["FCI", "StoredFCI"]


from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from . import Mercado, Moneda, Pais, PlazoLiquidacion, TipoInstrumento


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


# -------------------------------------------------
class StoredFCI(FCI):
    id: PydanticObjectId = Field(alias="_id")
