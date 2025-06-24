__all__ = ["OptionCoberedCallSummary", "OptionCoberedCallFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionCoberedCallSummary(BaseModel):
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
    reward_pct: float
    risk_pct: float
    reward_risk_ratio: float
    tna_adj: float
    risk_adj_tna: float


# --------------------------------------------------
class OptionCoberedCallFilter(BaseFilterParams):
    ticker: Optional[str] = None
