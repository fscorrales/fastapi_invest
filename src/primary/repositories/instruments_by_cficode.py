__all__ = ["InstrumentsByCFICodeRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredInstrumentByCFICode


class InstrumentsByCFICodeRepository(BaseRepository[StoredInstrumentByCFICode]):
    collection_name = "primary_instruments_by_cficode"
    model = StoredInstrumentByCFICode


InstrumentsByCFICodeRepositoryDependency = Annotated[
    InstrumentsByCFICodeRepository, Depends()
]
