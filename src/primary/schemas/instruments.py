__all__ = ["Instrument"]

from pydantic import BaseModel

from .common import CFICode, Enviroment, MarketID


# --------------------------------------------------
class Instrument(BaseModel):
    symbol: str
    marketId: MarketID
    cficode: CFICode
    enviroment: Enviroment
