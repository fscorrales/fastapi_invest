__all__ = ["WSMessageSubscription", "WSMarketData"]

from typing import List

from pydantic import BaseModel

from .common import Depth, Entry, Enviroment, InstrumentID, MarketID


class WSProductSubscription(BaseModel):
    symbol: str
    marketId: MarketID = MarketID.ROFX

class WSMessageSubscription(BaseModel):
    type: str = "smd"
    level: int = 1
    entries: List[Entry]
    products: List[WSProductSubscription]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class WSMarketData(InstrumentID):
    enviroment: Enviroment
