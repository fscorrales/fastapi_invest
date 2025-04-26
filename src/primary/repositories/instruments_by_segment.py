__all__ = ["InstrumentsBySegmentRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredInstrumentBySegment


class InstrumentsBySegmentRepository(BaseRepository[StoredInstrumentBySegment]):
    collection_name = "primary_instruments_by_segment"
    model = StoredInstrumentBySegment


InstrumentsBySegmentRepositoryDependency = Annotated[
    InstrumentsBySegmentRepository, Depends()
]
