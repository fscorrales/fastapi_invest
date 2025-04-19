__all__ = ["ParamsInstumentsBySegment", "InstrumentBySegment"]

from pydantic import BaseModel

from .common import Enviroment, InstrumentID, MarketID, MarketSegmentID


# --------------------------------------------------
class ParamsInstumentsBySegment(BaseModel):
    MarketSegmentID: MarketSegmentID
    MarketID: MarketID


# --------------------------------------------------
class InstrumentBySegment(InstrumentID):
    enviroment: Enviroment
