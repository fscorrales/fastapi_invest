__all__ = ["WSMessageSubscription", "WSMarketData", "WSProductSubscription"]

from typing import List

from pydantic import BaseModel

from .common import Depth, Entry, Enviroment, InstrumentID, MarketID


class WSProductSubscription(BaseModel):
    symbol: str
    marketId: MarketID = MarketID.rofex


class WSMessageSubscription(BaseModel):
    type: str = "smd"
    level: int = 1
    entries: List[Entry]
    products: List[WSProductSubscription]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class WSMarketData(InstrumentID):
    enviroment: Enviroment
