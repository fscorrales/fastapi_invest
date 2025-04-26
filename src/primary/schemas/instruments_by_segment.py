__all__ = [
    "InstrumentsBySegmentParams",
    "InstrumentBySegment",
    "StoredInstrumentBySegment",
    "InstrumentsBySegmentFilter",
]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import Enviroment, InstrumentID, MarketID, MarketSegmentID


# --------------------------------------------------
class InstrumentsBySegmentParams(BaseModel):
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
class InstrumentsBySegmentFilter(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    marketSegmentId: Optional[MarketSegmentID] = None
