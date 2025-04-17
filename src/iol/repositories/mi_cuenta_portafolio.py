__all__ = ["MiCuentaPortafolioRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import PosicionPortafolio


class MiCuentaPortafolioRepository(BaseRepository[PosicionPortafolio]):
    collection_name = "iol_mi_cuenta_portafolio"
    model = PosicionPortafolio


MiCuentaPortafolioRepositoryDependency = Annotated[
    MiCuentaPortafolioRepository, Depends()
]
