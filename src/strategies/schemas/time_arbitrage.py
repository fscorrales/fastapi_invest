__all__ = ["TimeArbitrageSummary", "TimeArbitrageFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class TimeArbitrageSummary(BaseModel):
    buy_sell: str
    cficode: str
    currency: str
    ticker: str
    ticker_buy: str
    ticker_sell: str
    buy_price: float
    sell_price: float
    q_max: float
    tna: float
    p_and_l: float
    days: int


# --------------------------------------------------
class TimeArbitrageFilter(BaseFilterParams):
    ticker: Optional[str] = None
