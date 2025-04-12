__all__ = ["TitulosFCIsRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import FCI


class TitulosFCIsRepository(BaseRepository[FCI]):
    collection_name = "iol_titulos_fcis"
    model = FCI


TitulosFCIsRepositoryDependency = Annotated[TitulosFCIsRepository, Depends()]
