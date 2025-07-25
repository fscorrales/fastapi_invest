__all__ = ["OptionMarketDataSummary", "OptionMarketDataFilter"]

from datetime import date
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
    type: Optional[str] = None
    expire: Optional[date] = None
    month_expire: Optional[str] = None
    days_expire: Optional[int] = None
    strike: Optional[float] = None
    underlying_ticker: Optional[str] = None
    underlying_close: Optional[float] = None


# --------------------------------------------------
class OptionMarketDataFilter(BaseFilterParams):
    ticker: Optional[str] = None
