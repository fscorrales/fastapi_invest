__all__ = [
    "RestMarketDataParams",
    "RestMarketData",
    "RestMarketDataDocument",
    "RestMarketDataFilter",
]

from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import Depth, Entry, Enviroment, MarketData, MarketID, SettlementTerm


# --------------------------------------------------
class RestMarketDataParams(BaseModel):
    marketId: MarketID
    symbol: str
    settlement_term: SettlementTerm
    entries: List[Entry] = ["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"]
    depth: Depth


# --------------------------------------------------
class RestMarketData(MarketData):
    symbol: str
    marketId: MarketID
    enviroment: Enviroment


# --------------------------------------------------
class RestMarketDataDocument(RestMarketData):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class RestMarketDataFilter(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    symbol: Optional[str] = None


# {
#     "marketId": "ROFX",
#     "symbol": "MERV - XMEV - GGAL - 24hs",
#     "entries": ["OP", "CL", "HI", "LO", "BI", "OF", "LA"],
#     "depth": 3,
# }
# {
#     "status": "OK",
#     "marketData": {
#         "OP": 7000,
#         "CL": {"price": 7070, "size": None, "date": 1744761600000},
#         "HI": 7050,
#         "OF": [
#             {"price": 6810, "size": 10008},
#             {"price": 6820, "size": 17243},
#             {"price": 6830, "size": 1001},
#         ],
#         "LO": 6690,
#         "BI": [
#             {"price": 6790, "size": 300},
#             {"price": 6780, "size": 47712},
#             {"price": 6770, "size": 5788},
#         ],
#         "LA": {"price": 6810, "size": 31, "date": 1745261638000},
#     },
#     "depth": 3,
#     "aggregated": True,
# }
