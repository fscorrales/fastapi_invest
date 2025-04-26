__all__ = ["InstrumentsBySegmentRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import InstrumentBySegmentDocument


class InstrumentsBySegmentRepository(BaseRepository[InstrumentBySegmentDocument]):
    collection_name = "primary_instruments_by_segment"
    model = InstrumentBySegmentDocument


InstrumentsBySegmentRepositoryDependency = Annotated[
    InstrumentsBySegmentRepository, Depends()
]
