__all__ = ["InstrumentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredInstrument


class InstrumentsRepository(BaseRepository[StoredInstrument]):
    collection_name = "primary_instruments"
    model = StoredInstrument


InstrumentsRepositoryDependency = Annotated[InstrumentsRepository, Depends()]
