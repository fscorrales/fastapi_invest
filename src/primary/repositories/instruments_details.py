__all__ = ["InstrumentsDetailsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import InstrumentDetailsDocument


class InstrumentsDetailsRepository(BaseRepository[InstrumentDetailsDocument]):
    collection_name = "primary_instruments_details"
    model = InstrumentDetailsDocument


InstrumentsDetailsRepositoryDependency = Annotated[
    InstrumentsDetailsRepository, Depends()
]
