__all__ = ["InstrumentsByCFICodeRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import InstrumentByCFICodeDocument


class InstrumentsByCFICodeRepository(BaseRepository[InstrumentByCFICodeDocument]):
    collection_name = "primary_instruments_by_cficode"
    model = InstrumentByCFICodeDocument


InstrumentsByCFICodeRepositoryDependency = Annotated[
    InstrumentsByCFICodeRepository, Depends()
]
