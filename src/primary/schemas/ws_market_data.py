__all__ = [
    "WSMarketDataParams",
    "WSMarketData",
    "WSProductSubscription",
    "WSProductSubscription",
]

from typing import List

from pydantic import BaseModel

from .common import (
    Depth,
    Entry,
    Enviroment,
    InstrumentID,
    MarketData,
    MarketID,
    SettlementTerm,
)


# --------------------------------------------------
class WSProductSubscription(BaseModel):
    symbol: str
    marketId: MarketID = MarketID.rofex


# --------------------------------------------------
class WSMarketDataParams(BaseModel):
    symbols: List[str] = None
    settlement_terms: List[SettlementTerm] = None
    marketId: MarketID = MarketID.rofex
    entries: List[Entry]
    # products: List[WSProductSubscription]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class WSMarketData(MarketData):
    pass


# --------------------------------------------------
class WSFullMessage(BaseModel):
    type: str = "Md"
    timestamp: int  # Timestamp in milliseconds since epoch
    instrumentId: InstrumentID
    marketData: WSMarketData
    enviroment: Enviroment = Enviroment.live  # Environment (default: LIVE)


# 📥 Recibido:
# {
#     "type": "Md",
#     "timestamp": 1745435899242,
#     "instrumentId": {"marketId": "ROFX", "symbol": "MERV - XMEV - GGAL - CI"},
#     "marketData": {
#         "LO": 7490,
#         "NV": 169669,
#         "BI": [{"price": 7620, "size": 2494}, {"price": 7610, "size": 1626}],
#         "OF": [{"price": 7630, "size": 130}, {"price": 7640, "size": 24}],
#         "EV": 1294330050,
#         "CL": {"price": 7230, "date": 1745280000000},
#         "LA": {"price": 7620, "size": 100, "date": 1745435898000},
#         "OP": 7490,
#         "HI": 7710,
#     },
# }
