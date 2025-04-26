__all__ = ["SegmentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import SegmentDocument


class SegmentsRepository(BaseRepository[SegmentDocument]):
    collection_name = "primary_segments"
    model = SegmentDocument


SegmentsRepositoryDependency = Annotated[SegmentsRepository, Depends()]
