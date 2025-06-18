__all__ = ["OptionMarketDataSummary", "OptionMarketDataFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionMarketDataSummary(BaseModel):
    ticker: str
    bid_size: Optional[float] = None
    bid: Optional[float] = None
    last: Optional[float] = None
    ask: Optional[float] = None
    ask_size: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    chg_pct: Optional[float] = None
    volume: Optional[float] = None
    nom_volumne: Optional[float] = None
    days_expire: int
    strike: float
    underlying_ticker: str
    underlying_close: float


# --------------------------------------------------
class OptionMarketDataFilter(BaseFilterParams):
    ticker: Optional[str] = None
