__all__ = [
    "InstrumentDetails",
    "InstrumentDetailsParams",
    "InstrumentDetailsDocument",
    "InstrumentsDetailsFilter",
    "CurrencySettlement",
]

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel
from pydantic_mongo import PydanticObjectId

from ...utils import BaseFilterParams
from .common import (
    CFICode,
    Enviroment,
    MarketID,
    MarketSegmentID,
    OrderTimeInForce,
    OrderType,
    SettlementTerm,
)


# --------------------------------------------------
class InstrumentDetailsParams(BaseModel):
    marketId: MarketID | None = None
    symbol: str | None = None


# --------------------------------------------------
class TickPriceRange(BaseModel):
    lowerLimit: float | None
    upperLimit: float | None
    tick: float | None


# --------------------------------------------------
class TickPriceRanges(RootModel[dict[str, TickPriceRange]]):
    pass


# -------------------------------------------------
class CurrencySettlement(str, Enum):
    ars_ci = "ars_ci"
    ars_24hs = "ars_24hs"
    ars_48hs = "ars_48hs"
    ars_72hs = "ars_72hs"
    mep_ci = "mep_ci"
    mep_24hs = "mep_24hs"
    mep_48hs = "mep_48hs"
    mep_72hs = "mep_72hs"
    ccl_ci = "ccl_ci"
    ccl_24hs = "ccl_24hs"
    ccl_48hs = "ccl_48hs"
    ccl_72hs = "ccl_72hs"


# --------------------------------------------------
class InstrumentDetails(BaseModel):
    symbol: str
    ticker: Optional[str]
    settlement: Optional[SettlementTerm]
    marketId: MarketID
    marketSegmentId: MarketSegmentID
    lowLimitPrice: float | None
    highLimitPrice: float | None
    minPriceIncrement: float
    minTradeVol: float
    maxTradeVol: float
    tickSize: float
    contractMultiplier: float
    roundLot: float
    priceConvertionFactor: float
    maturityDate: int | None
    currency: str
    currency_settlement: Optional[CurrencySettlement]
    orderTypes: List[OrderType]
    timesInForce: List[OrderTimeInForce]
    securityType: str | None
    settlType: str | None
    instrumentPricePrecision: int
    instrumentSizePrecision: int
    securityId: str | None
    securityIdSource: str | None
    securityDescription: str
    tickPriceRanges: TickPriceRanges
    strike: float | None
    underlying: Optional[str]
    cficode: CFICode
    enviroment: Enviroment


# -------------------------------------------------
class InstrumentDetailsDocument(InstrumentDetails):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class InstrumentsDetailsFilter(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
    marketId: Optional[MarketID] = None
    marketSegmentId: Optional[MarketSegmentID] = None
    cficode: Optional[CFICode] = None
