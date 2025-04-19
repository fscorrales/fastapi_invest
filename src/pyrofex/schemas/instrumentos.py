__all__ = ["Instrumento"]

from pydantic import BaseModel

from .common import CFICode, Enviroment, MarketID


# --------------------------------------------------
class Instrumento(BaseModel):
    symbol: str
    marketId: MarketID
    cficode: CFICode
    enviroment: Enviroment
