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

# 📥 Recibido: 
# {"type":"Md","timestamp":1745333061575,"instrumentId":{"marketId":"ROFX","symbol":"MERV - XMEV - GGAL - 24hs"},"marketData":{"OP":6880,"CL":{"price":6840,"date":1745193600000},"LO":6880,"BI":[{"price":7130,"size":14026}],"HI":7150,"OF":[{"price":7150,"size":5430}]}}