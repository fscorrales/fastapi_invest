__all__ = ["Instrument", "InstrumentDocument", "InstrumentsFilter"]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import CFICode, Enviroment, MarketID


# --------------------------------------------------
class Instrument(BaseModel):
    symbol: str
    marketId: MarketID
    cficode: CFICode
    enviroment: Enviroment


# -------------------------------------------------
class InstrumentDocument(Instrument):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class InstrumentsFilter(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    cficode: Optional[CFICode] = None
