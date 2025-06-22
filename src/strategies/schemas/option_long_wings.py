__all__ = ["OptionLongWingsSummary", "OptionLongWingsFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionLongWingsSummary(BaseModel):
    underlying_ticker: str
    days_expire: int
    ticker: str
    tna_total: float
    min_invest: float
    protection_pct: float
    tna: float
    tna_extra: float
    var_tna_extra: float
    pe: float
    var_pe: float
    ve_pct: float
    bid_size: float
    bid_price: float
    last_price: Optional[float] = None
    strike: float
    underlying_close: float
    vi: float
    ve: float
    tna_caucion: float


# --------------------------------------------------
class OptionLongWingsFilter(BaseFilterParams):
    ticker: Optional[str] = None
