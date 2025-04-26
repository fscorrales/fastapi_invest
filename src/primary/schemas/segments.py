__all__ = ["Segment", "StoredSegment", "SegmentsFilter"]

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import Enviroment, MarketID, MarketSegmentID


# --------------------------------------------------
class Segment(BaseModel):
    enviroment: Enviroment
    marketSegmentId: MarketSegmentID
    marketId: MarketID


# -------------------------------------------------
class StoredSegment(Segment):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class SegmentsFilter(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    marketSegmentId: Optional[MarketSegmentID] = None
