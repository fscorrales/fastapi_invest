__all__ = ["SegmentsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import Segment


class SegmentsRepository(BaseRepository[Segment]):
    collection_name = "primary_segments"
    model = Segment


SegmentsRepositoryDependency = Annotated[SegmentsRepository, Depends()]
