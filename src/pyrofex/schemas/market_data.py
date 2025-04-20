__all__ = ["ParamsMarketData", "MarketData"]

from typing import List

from pydantic import BaseModel

from .common import Depth, Entry, Enviroment, InstrumentID, MarketID


class ParamsMarketData(BaseModel):
    marketId: MarketID
    symbol: str
    entries: List[Entry]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class MarketData(InstrumentID):
    enviroment: Enviroment
