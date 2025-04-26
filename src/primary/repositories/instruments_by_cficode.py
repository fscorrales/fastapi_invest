__all__ = ["InstrumentsByCFICodeRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredInstrumentBySegment


class InstrumentsByCFICodeRepository(BaseRepository[StoredInstrumentBySegment]):
    collection_name = "primary_instruments_by_cficode"
    model = StoredInstrumentBySegment


InstrumentsByCFICodeRepositoryDependency = Annotated[
    InstrumentsByCFICodeRepository, Depends()
]
