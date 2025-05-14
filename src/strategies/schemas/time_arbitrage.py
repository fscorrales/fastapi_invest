__all__ = ["TimeArbitrageSummary"]

from pydantic import BaseModel


# --------------------------------------------------
class TimeArbitrageSummary(BaseModel):
    buy_sell: str
    cficode: str
    ticker_buy: str
    ticker_sell: str
    q_max: int
    tna: float
    days: int
