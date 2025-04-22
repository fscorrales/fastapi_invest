__all__ = ["InstrumentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import Instrument


class InstrumentsRepository(BaseRepository[Instrument]):
    collection_name = "primary_instruments"
    model = Instrument


InstrumentsRepositoryDependency = Annotated[InstrumentsRepository, Depends()]
