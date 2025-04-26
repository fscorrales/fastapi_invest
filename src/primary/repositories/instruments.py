__all__ = ["InstrumentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import InstrumentDocument


class InstrumentsRepository(BaseRepository[InstrumentDocument]):
    collection_name = "primary_instruments"
    model = InstrumentDocument


InstrumentsRepositoryDependency = Annotated[InstrumentsRepository, Depends()]
