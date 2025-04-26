__all__ = ["InstrumentsByCFICodeService", "InstrumentsByCFICodeServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ...utils import BaseFilterParams
from ..handlers import get_instruments_by_cficode, get_token
from ..repositories import (
    InstrumentsByCFICodeRepositoryDependency,
)
from ..schemas import (
    InstrumentByCFICode,
    InstrumentByCFICodeDocument,
    InstrumentsByCFICodeParams,
    PrimaryCredentials,
    SyncResult,
)


# -------------------------------------------------
@dataclass
class InstrumentsByCFICodeService:
    instruments: InstrumentsByCFICodeRepositoryDependency

    # -------------------------------------------------
    async def sync_instruments_by_cficode_from_primary(
        self,
        credentials: PrimaryCredentials,
        params: InstrumentsByCFICodeParams = None,
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

                fields = await get_instruments_by_cficode(
                    primary=connect_primary, params=params, httpxAsyncClient=c
                )

                data_to_store = [
                    InstrumentByCFICode(**field.model_dump()) for field in fields
                ]

                delete_dict = {
                    "enviroment": credentials.enviroment,
                    "cficode": params.CFICode,
                }

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
    async def get_instruments_by_cficode_from_db(
        self, params: BaseFilterParams
    ) -> List[InstrumentByCFICodeDocument]:
        try:
            return await self.instruments.find_with_filter_params(params=params)
        except Exception as e:
            logger.error(
                f"Error retrieving Primary's Instruments By CFICode from database: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Instruments By CFICode from the database",
            )


InstrumentsByCFICodeServiceDependency = Annotated[
    InstrumentsByCFICodeService, Depends()
]
