__all__ = ["InstrumentsDetailsService", "InstrumentsDetailsServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import get_instruments_details, get_token
from ..repositories import (
    InstrumentsDetailsRepositoryDependency,
)
from ..schemas import InstrumentDetails, ParamsInstumentDetails, StoredInstrumentDetails, SyncResult
from ...utils import BaseFilterParams


# -------------------------------------------------
@dataclass
class InstrumentsDetailsService:
    instruments: InstrumentsDetailsRepositoryDependency

    # -------------------------------------------------
    async def sync_instruments_details_from_primary(
        self,
        username: str,
        password: str,
        url: str,
        params: ParamsInstumentDetails = None,
        enviroment: str = "REMARKETS",
    ) -> SyncResult:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_primary = await get_token(
                    username, password, url, httpxAsyncClient=c
                )
                # Intentar obtener el estado de cuenta
                fields = await get_instruments_details(
                    primary=connect_primary, params=params, httpxAsyncClient=c
                )

                data_to_store = [
                    InstrumentDetails(**field.model_dump()) for field in fields
                ]

                # Contar los instrumentos existentes antes de eliminarlos
                deleted_count = await self.instruments.count_by_fields(
                    {"enviroment": enviroment}
                )
                await self.instruments.delete_by_fields(
                    {"enviroment": enviroment}
                )  # Eliminar el portafolio anterior
                await self.instruments.save_all(data_to_store)

                return {
                    "added": len(data_to_store),
                    "deleted": deleted_count,
                    "enviroment": enviroment,
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
    async def get_instruments_details_from_db(self, params: BaseFilterParams) -> List[StoredInstrumentDetails]:
        try:
            return await self.instruments.find_with_filter_params(params=params)
        except Exception as e:
            logger.error(
                f"Error retrieving Primary's Instruments Details from database: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Instruments Details from the database",
            )


InstrumentsDetailsServiceDependency = Annotated[InstrumentsDetailsService, Depends()]
