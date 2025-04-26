__all__ = [
    "ParamsInstumentsByCFICode",
    "InstrumentByCFICode",
    "StoredInstrumentByCFICode",
    "FilterParamsInstrumentsByCFICode",
]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import CFICode, Enviroment, InstrumentID, MarketID


# --------------------------------------------------
class ParamsInstumentsByCFICode(BaseModel):
    CFICode: CFICode


# --------------------------------------------------
class InstrumentByCFICode(InstrumentID):
    enviroment: Enviroment
    cficode: CFICode


# --------------------------------------------------
class StoredInstrumentByCFICode(InstrumentByCFICode):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class FilterParamsInstrumentsByCFICode(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    cficode: Optional[CFICode] = None
    marketId: Optional[MarketID] = None
