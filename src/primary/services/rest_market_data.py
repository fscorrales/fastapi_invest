__all__ = ["RestMarketDataService", "RestMarketDataServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ...utils import BaseFilterParams
from ..handlers import get_rest_market_data, get_token
from ..repositories import (
    RestMarketDataRepositoryDependency,
)
from ..schemas import (
    PrimaryCredentials,
    RestMarketData,
    RestMarketDataDocument,
    RestMarketDataParams,
    SyncResult,
)


# -------------------------------------------------
@dataclass
class RestMarketDataService:
    market_data: RestMarketDataRepositoryDependency

    # -------------------------------------------------
    async def sync_rest_market_data_from_primary(
        self,
        credentials: PrimaryCredentials,
        params: RestMarketDataParams = None,
    ) -> SyncResult:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_primary = await get_token(
                    credentials.username,
                    credentials.password,
                    credentials.url,
                    httpxAsyncClient=c,
                )

                fields = await get_rest_market_data(
                    primary=connect_primary, params=params, httpxAsyncClient=c
                )

                data_to_store = [
                    RestMarketData(**field.model_dump()) for field in fields
                ]

                delete_dict = {
                    "enviroment": credentials.enviroment,
                    "marketId": params.MarketID,
                    "symbol": params.symbol,
                }
                # Contar los instrumentos existentes antes de eliminarlos
                deleted_count = await self.market_data.count_by_fields(delete_dict)
                await self.market_data.delete_by_fields(
                    delete_dict
                )  # Eliminar el portafolio anterior
                await self.market_data.save_all(data_to_store)

                return {
                    "added": len(data_to_store),
                    "deleted": deleted_count,
                    "enviroment": credentials.enviroment,
                }
            except ValidationError as e:
                logger.error(f"Validation Error: {e}")
                raise HTTPException(
                    status_code=400, detail="Invalid response format from Primary"
                )
            except Exception as e:
                logger.error(f"Error during report processing: {e}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials or unable to authenticate",
                )

    # -------------------------------------------------
    async def get_rest_market_data_from_db(
        self, params: BaseFilterParams
    ) -> List[RestMarketDataDocument]:
        try:
            return await self.market_data.find_with_filter_params(params=params)
        except Exception as e:
            logger.error(
                f"Error retrieving Primary's Rest Market Data from database: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Rest Market Data from the database",
            )


RestMarketDataServiceDependency = Annotated[RestMarketDataService, Depends()]
