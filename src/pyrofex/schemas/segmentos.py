__all__ = ["Segmento"]

from pydantic import BaseModel


# --------------------------------------------------
class Segmento(BaseModel):
    enviroment: str
    marketSegmentId: str
    marketId: str
