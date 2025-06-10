__all__ = ["OptionSpreadSummary", "OptionSpreadFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionSpreadSummary(BaseModel):
    underlying_ticker: str
    type: str
    days_expire: int
    ticker_x0: str
    ticker_x1: str
    tna_max_profit: float
    min_invest: float
    tna_max_diff: float
    var_max_loss: float
    var_pe: float
    var_max_profit: float
    spread_pct: float
    strike_x0: float
    strike_x1: float
    prima_x0: float
    size_x0: float
    size_x1: float
    prima_x1: float
    underlying_close: float
    prima_neta: float
    spread: float
    pe: float
    max_profit: float
    max_profit_pct: float
    max_loss: float
    max_loss_pct: float
    tna_max_loss: float
    round_var_max_profit: float


# --------------------------------------------------
class OptionSpreadFilter(BaseFilterParams):
    ticker_x0: Optional[str] = None
    ticker_x1: Optional[str] = None
