__all__ = ["OptionLongWingsSummary", "OptionLongWingsFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionLongWingsSummary(BaseModel):
    underlying_ticker: str
    type: str
    days_expire: int
    min_invest: float
    max_profit: float
    var_max_profit: float
    max_loss: float
    spread_pe_inf_sup: float
    q_bull: float
    q_bear: float
    ticker_x0: str
    ticker_x1: str
    ticker_x2: str
    ticker_x3: str
    prima_x0: float
    prima_x1: float
    prima_x2: float
    prima_x3: float
    underlying_close: float
    prima_neta: float
    pe_max_profit: float
    pe_inf: float
    pe_sup: float
    var_pe_inf: float
    var_pe_sup: float
    var_max_loss_inf: float
    var_max_loss_sup: float
    strike_x0: float
    strike_x1: float
    strike_x2: float
    strike_x3: float


# --------------------------------------------------
class OptionLongWingsFilter(BaseFilterParams):
    ticker: Optional[str] = None
