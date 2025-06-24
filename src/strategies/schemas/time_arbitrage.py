__all__ = ["TimeArbitrageSummary", "TimeArbitrageFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class TimeArbitrageSummary(BaseModel):
    buy_sell: str
    cficode: str
    currency: str
    ticker_buy: str
    ticker_sell: str
    buy_price: float
    sell_price: float
    q_max: float
    tna: float
    p_and_l: float
    tna_operation: float
    tna_caucion: float
    days: int
    reward_pct: float
    risk_pct: float
    reward_risk_ratio: float
    tna_adj: float
    risk_adj_tna: float


# --------------------------------------------------
class TimeArbitrageFilter(BaseFilterParams):
    ticker: Optional[str] = None
