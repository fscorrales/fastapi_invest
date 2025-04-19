__all__ = ["Segmento"]

from pydantic import BaseModel

from .common import Enviroment, MarketID, MarketSegmentID


# --------------------------------------------------
class Segmento(BaseModel):
    enviroment: Enviroment
    marketSegmentId: MarketSegmentID
    marketId: MarketID
