__all__ = ["WSMessageSubscription", "WSMarketData", "WSProductSubscription"]

from typing import List, Optional

from pydantic import BaseModel

from .common import Depth, Entry, Enviroment, InstrumentID, MarketID


# --------------------------------------------------
class WSProductSubscription(BaseModel):
    symbol: str
    marketId: MarketID = MarketID.rofex


# --------------------------------------------------
class WSMessageSubscription(BaseModel):
    type: str = "smd"
    level: int = 1
    entries: List[Entry]
    products: List[WSProductSubscription]
    depth: Depth = Depth.level_1


# --------------------------------------------------
class PriceWithSize(BaseModel):
    price: float
    size: int


# --------------------------------------------------
class PriceWithSizeAndDate(PriceWithSize):
    size: Optional[int] = None  # Size of the last trade
    date: Optional[int] = None  # Timestamp in milliseconds since epoch


# --------------------------------------------------
class WSMarketData(BaseModel):
    NV: Optional[int] = None  # Notional Value
    BI: Optional[List[PriceWithSize]] = None  # Bid depends on the depth
    OF: Optional[List[PriceWithSize]] = None  # Offer depends on the depth
    EV: Optional[float] = None  # Effective Value
    CL: Optional[PriceWithSizeAndDate] = None  # Previous Close
    LA: Optional[PriceWithSizeAndDate] = None  # Last Trade
    OP: Optional[float] = None  # Opening Price
    HI: Optional[float] = None  # Highest Price
    LO: Optional[float] = None  # Lowest Price
    TV: Optional[int] = None  # Volumen operado en contratos/nominales (null value)
    SE: Optional[float] = None  # Precio de ajuste (solo para futuros)
    OI: Optional[float] = None  # Interés abierto (solo para futuros)
    IV: Optional[float] = None  # Valor del índice (solo para índices)
    ACP: Optional[float] = (
        None  # Precio de cierre del día de la fecha para instrumentos externos a MATBA ROFEX
    )


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
