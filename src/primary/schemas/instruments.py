__all__ = ["Instrument", "StoredInstrument", "FilterParamsInstruments"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from .common import CFICode, Enviroment, MarketID


# --------------------------------------------------
class Instrument(BaseModel):
    symbol: str
    marketId: MarketID
    cficode: CFICode
    enviroment: Enviroment


# -------------------------------------------------
class StoredInstrument(Instrument):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class FilterParamsInstruments(BaseFilterParams):
    enviroment: Optional[Enviroment] = None