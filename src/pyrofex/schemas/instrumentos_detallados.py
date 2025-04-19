__all__ = ["InstrumentoDetallado", "ParamsInstumentoDetallado"]

from typing import List

from pydantic import BaseModel, RootModel

from .common import (
    CFICode,
    Enviroment,
    MarketID,
    MarketSegmentID,
    OrderTimeInForce,
    OrderType,
)


# --------------------------------------------------
class ParamsInstumentoDetallado(BaseModel):
    marketId: MarketID
    symbol: str


# --------------------------------------------------
class TickPriceRange(BaseModel):
    lowerLimit: float | None
    upperLimit: float | None
    tick: float | None


# --------------------------------------------------
class TickPriceRanges(RootModel[dict[str, TickPriceRange]]):
    pass


# --------------------------------------------------
class InstrumentoDetallado(BaseModel):
    symbol: str
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
    underlying: str
    cficode: CFICode
    enviroment: Enviroment
