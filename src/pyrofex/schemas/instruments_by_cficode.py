__all__ = ["ParamsInstumentsByCFICode", "InstrumentByCFICode"]

from pydantic import BaseModel

from .common import CFICode, Enviroment, InstrumentID


# --------------------------------------------------
class ParamsInstumentsByCFICode(BaseModel):
    CFICode: CFICode


# --------------------------------------------------
class InstrumentByCFICode(InstrumentID):
    enviroment: Enviroment
