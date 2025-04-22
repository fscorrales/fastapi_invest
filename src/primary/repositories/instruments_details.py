__all__ = ["InstrumentsDetailsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import InstrumentDetails


class InstrumentsDetailsRepository(BaseRepository[InstrumentDetails]):
    collection_name = "primary_instruments_details"
    model = InstrumentDetails


InstrumentsDetailsRepositoryDependency = Annotated[
    InstrumentsDetailsRepository, Depends()
]
