__all__ = ["SegmentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import StoredSegment


class SegmentsRepository(BaseRepository[StoredSegment]):
    collection_name = "primary_segments"
    model = StoredSegment


SegmentsRepositoryDependency = Annotated[SegmentsRepository, Depends()]
