__all__ = ["Segment"]

from pydantic import BaseModel

from .common import Enviroment, MarketID, MarketSegmentID


# --------------------------------------------------
class Segment(BaseModel):
    enviroment: Enviroment
    marketSegmentId: MarketSegmentID
    marketId: MarketID
