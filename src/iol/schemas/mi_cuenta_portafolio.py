__all__ = ["PosicionPortafolio", "StoredPosicionPortafolio"]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from . import Mercado, Moneda, Pais, PlazoLiquidacion, TipoInstrumento


# -------------------------------------------------
class TituloEnCartera(BaseModel):
    simbolo: Optional[str]
    descripcion: Optional[str]
    pais: Optional[Pais]
    mercado: Optional[Mercado]
    tipo: Optional[TipoInstrumento]
    plazo: Optional[PlazoLiquidacion]
    moneda: Optional[Moneda]


# -------------------------------------------------
class PosicionPortafolio(BaseModel):
    pais: Optional[Pais]
    cantidad: Optional[float]
    comprometido: Optional[float]
    puntosVariacion: Optional[float]
    variacionDiaria: Optional[float]
    ultimoPrecio: Optional[float]
    ppc: Optional[float]
    gananciaPorcentaje: Optional[float]
    gananciaDinero: Optional[float]
    valorizado: Optional[float]
    titulo: Optional[TituloEnCartera]
    parking: Optional[int] = None


# -------------------------------------------------
class StoredPosicionPortafolio(PosicionPortafolio):
    id: PydanticObjectId = Field(alias="_id")
