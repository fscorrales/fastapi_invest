__all__ = ["RestMarketDataRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import RestMarketDataDocument


class RestMarketDataRepository(BaseRepository[RestMarketDataDocument]):
    collection_name = "primary_rest_market_data"
    model = RestMarketDataDocument


RestMarketDataRepositoryDependency = Annotated[RestMarketDataRepository, Depends()]
