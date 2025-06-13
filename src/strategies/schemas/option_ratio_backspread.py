__all__ = ["OptionRatioBackspreadSummary", "OptionRatioBackspreadFilter"]

from typing import Optional

from pydantic import BaseModel

from ...utils import BaseFilterParams


# --------------------------------------------------
class OptionRatioBackspreadSummary(BaseModel):
    underlying_ticker: str
    type: str
    days_expire: int
    ticker_x0: str
    ticker_x1: str
    var_pe_sup: float
    spread_pe_sup_inf: float
    min_invest: float
    max_loss: float
    prima_x0: float
    q_venta: float
    q_compra: float
    prima_x1: float
    max_loss_pct: float
    var_pe_max_loss: float
    strike_x0: float
    strike_x1: float
    size_x0: float
    size_x1: float
    underlying_close: float
    pe_sup: float
    pe_max_loss: float
    pe_inf: float
    var_pe_inf: float
    prima_neta: float
    spread: float


# --------------------------------------------------
class OptionRatioBackspreadFilter(BaseFilterParams):
    ticker_x0: Optional[str] = None
    ticker_x1: Optional[str] = None
