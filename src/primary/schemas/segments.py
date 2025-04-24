__all__ = ["Segment", "StoredSegment", "FilterParamsSegments"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from .common import Enviroment, MarketID, MarketSegmentID
from ...utils import BaseFilterParams
from typing import Optional


# --------------------------------------------------
class Segment(BaseModel):
    enviroment: Enviroment
    marketSegmentId: MarketSegmentID
    marketId: MarketID


# -------------------------------------------------
class StoredSegment(Segment):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class FilterParamsSegments(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
