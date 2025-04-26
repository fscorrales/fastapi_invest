__all__ = ["ParamsMarketData", "MarketData"]

from typing import List

from pydantic import BaseModel

from .common import Depth, Entry, Enviroment, MarketData, MarketID


# --------------------------------------------------
class ParamsMarketData(BaseModel):
    marketId: MarketID
    symbol: str
    entries: List[Entry]
    depth: Depth = Depth.level_1  # Affects only to BI, OF entries.


# --------------------------------------------------
class RestMarketData(MarketData):
    enviroment: Enviroment


{
    "marketId": "ROFX",
    "symbol": "MERV - XMEV - GGAL - 24hs",
    "entries": ["OP", "CL", "HI", "LO", "BI", "OF", "LA"],
    "depth": 3,
}
{
    "status": "OK",
    "marketData": {
        "OP": 7000,
        "CL": {"price": 7070, "size": None, "date": 1744761600000},
        "HI": 7050,
        "OF": [
            {"price": 6810, "size": 10008},
            {"price": 6820, "size": 17243},
            {"price": 6830, "size": 1001},
        ],
        "LO": 6690,
        "BI": [
            {"price": 6790, "size": 300},
            {"price": 6780, "size": 47712},
            {"price": 6770, "size": 5788},
        ],
        "LA": {"price": 6810, "size": 31, "date": 1745261638000},
    },
    "depth": 3,
    "aggregated": True,
}
