__all__ = [
    "InstrumentDetails",
    "ParamsInstumentDetails",
    "StoredInstrumentDetails",
    "FilterParamsInstrumentsDetails",
]

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
)


# --------------------------------------------------
class ParamsInstumentDetails(BaseModel):
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


# --------------------------------------------------
class InstrumentDetails(BaseModel):
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


# -------------------------------------------------
class StoredInstrumentDetails(InstrumentDetails):
    id: PydanticObjectId = Field(alias="_id")


# -------------------------------------------------
class FilterParamsInstrumentsDetails(BaseFilterParams):
    enviroment: Optional[Enviroment] = None
