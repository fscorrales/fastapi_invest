__all__ = ["InstrumentsDetailsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredInstrumentDetails


class InstrumentsDetailsRepository(BaseRepository[StoredInstrumentDetails]):
    collection_name = "primary_instruments_details"
    model = StoredInstrumentDetails


InstrumentsDetailsRepositoryDependency = Annotated[
    InstrumentsDetailsRepository, Depends()
]
