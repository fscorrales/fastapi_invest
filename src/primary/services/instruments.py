__all__ = ["InstrumentsService", "InstrumentsServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ...utils import BaseFilterParams
from ..handlers import get_instruments, get_token
from ..repositories import (
    InstrumentsRepositoryDependency,
)
from ..schemas import Instrument, PrimaryCredentials, StoredInstrument, SyncResult


# -------------------------------------------------
@dataclass
class InstrumentsService:
    instruments: InstrumentsRepositoryDependency

    # -------------------------------------------------
    async def sync_instruments_from_primary(
        self, credentials: PrimaryCredentials
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

                fields = await get_instruments(
                    primary=connect_primary, httpxAsyncClient=c
                )

                data_to_store = [Instrument(**field.model_dump()) for field in fields]

                delete_dict = {"enviroment": credentials.enviroment}
                # Contar los instrumentos existentes antes de eliminarlos
                deleted_count = await self.instruments.count_by_fields(delete_dict)
                await self.instruments.delete_by_fields(
                    delete_dict
                )  # Eliminar el portafolio anterior
                await self.instruments.save_all(data_to_store)

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
    async def get_instruments_from_db(
        self, params: BaseFilterParams
    ) -> List[StoredInstrument]:
        try:
            return await self.instruments.find_with_filter_params(params=params)
        except Exception as e:
            logger.error(f"Error retrieving Primary's Instruments from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Instruments from the database",
            )


InstrumentsServiceDependency = Annotated[InstrumentsService, Depends()]
