__all__ = [
    "WSMarketDataParams",
    "WSMarketData",
    "WSProductSubscription",
    "WSMarketDataSubscription",
    "WSFullMessage",
    "WSMarketDataDF",
]

from typing import List, Optional

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
    symbol: str  # For example "MERV - XMEV - GGAL - CI"
    marketId: MarketID = MarketID.rofex


# --------------------------------------------------
class WSMarketDataSubscription(BaseModel):
    type: str = "smd"
    level: int = 1
    entries: List[Entry] = ["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"]
    products: List[WSProductSubscription]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class WSMarketDataParams(BaseModel):
    tickers: List[str] = None
    settlement_terms: List[SettlementTerm] = None
    marketId: MarketID = MarketID.rofex
    entries: List[Entry] = ["LA", "BI", "OF", "NV", "EV", "OP", "CL", "HI", "LO"]
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


# --------------------------------------------------
class WSMarketDataDF(BaseModel):
    instrument: str
    timestamp: Optional[int]
    symbol: Optional[str]
    settlement: Optional[str]
    last_price: Optional[float]
    last_size: Optional[float]
    bid_price: Optional[float]
    bid_size: Optional[float]
    offer_price: Optional[float]
    offer_size: Optional[float]
    notional_value: Optional[float]
    effective_value: Optional[float]
    open: Optional[float]
    close_prev: Optional[float]
    high: Optional[float]
    low: Optional[float]
    tv: Optional[float]
    se: Optional[float]
    oi: Optional[float]
    iv: Optional[float]
    acp: Optional[float]

    class Config:
        from_attributes = True  # Permite la conversión de modelos ORM a Pydantic
