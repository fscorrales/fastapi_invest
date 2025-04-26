__all__ = ["SegmentsService", "SegmentsServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ...utils import BaseFilterParams
from ..handlers import get_segments, get_token
from ..repositories import (
    SegmentsRepositoryDependency,
)
from ..schemas import PrimaryCredentials, Segment, SegmentDocument, SyncResult


# -------------------------------------------------
@dataclass
class SegmentsService:
    segments: SegmentsRepositoryDependency

    # -------------------------------------------------
    async def sync_segments_from_primary(
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
                # Intentar obtener el estado de cuenta
                fields = await get_segments(primary=connect_primary, httpxAsyncClient=c)

                data_to_store = [Segment(**field.model_dump()) for field in fields]

                delete_dict = {"enviroment": credentials.enviroment}
                # Contar los instrumentos existentes antes de eliminarlos
                deleted_count = await self.segments.count_by_fields(delete_dict)
                await self.segments.delete_by_fields(
                    delete_dict
                )  # Eliminar el portafolio anterior

                await self.segments.save_all(data_to_store)

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
    async def get_segments_from_db(
        self, params: BaseFilterParams
    ) -> List[SegmentDocument]:
        try:
            return await self.segments.find_with_filter_params(params=params)
        except Exception as e:
            logger.error(f"Error retrieving Primary's Segments from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Segments from the database",
            )


SegmentsServiceDependency = Annotated[SegmentsService, Depends()]
