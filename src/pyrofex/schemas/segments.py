__all__ = ["Segment", "StoredSegment"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from .common import Enviroment, MarketID, MarketSegmentID


# --------------------------------------------------
class Segment(BaseModel):
    enviroment: Enviroment
    marketSegmentId: MarketSegmentID
    marketId: MarketID

# -------------------------------------------------
class StoredSegment(Segment):
    id: PydanticObjectId = Field(alias="_id")
