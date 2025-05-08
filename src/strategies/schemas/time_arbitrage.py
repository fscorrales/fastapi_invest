__all__ = ["TimeArbitrageSummary"]

from pydantic import BaseModel


# --------------------------------------------------
class TimeArbitrageSummary(BaseModel):
    buy_sell: str
    symbol_buy: str
    symbol_sell: str
    q_max: int
    tna: float
    days: int
