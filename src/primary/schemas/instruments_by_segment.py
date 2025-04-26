__all__ = [
    "ParamsInstumentsBySegment",
    "InstrumentBySegment",
    "StoredInstrumentBySegment",
    "FilterParamsInstrumentsBySegment",
]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import Enviroment, InstrumentID, MarketID, MarketSegmentID


# --------------------------------------------------
class ParamsInstumentsBySegment(BaseModel):
    MarketID: MarketID
    MarketSegmentID: MarketSegmentID


# --------------------------------------------------
class InstrumentBySegment(InstrumentID):
    marketSegmentId: MarketSegmentID
    enviroment: Enviroment


# --------------------------------------------------
class StoredInstrumentBySegment(InstrumentBySegment):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class FilterParamsInstrumentsBySegment(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    marketSegmentId: Optional[MarketSegmentID] = None
