__all__ = ["InstrumentsService", "InstrumentsServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import get_instruments, get_token
from ..repositories import (
    InstrumentsRepositoryDependency,
)
from ..schemas import Instrument, StoredInstrument


# -------------------------------------------------
@dataclass
class InstrumentsService:
    instruments: InstrumentsRepositoryDependency

    # -------------------------------------------------
    async def sync_instruments_from_primary(
        self, username: str, password: str, url: str, enviroment: str = "REMARKETS"
    ) -> List[Instrument]:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_primary = await get_token(
                    username, password, url, httpxAsyncClient=c
                )
                # Intentar obtener el estado de cuenta
                fields = await get_instruments(
                    primary=connect_primary, httpxAsyncClient=c
                )

                data_to_store = [Instrument(**field.model_dump()) for field in fields]

                await self.instruments.delete_by_fields(
                    {"enviroment": enviroment}
                )  # Eliminar el portafolio anterior
                await self.instruments.save_all(data_to_store)

                return fields
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
    async def get_instruments_from_db(self) -> List[StoredInstrument]:
        try:
            return await self.instruments.get_all()
        except Exception as e:
            logger.error(f"Error retrieving Primary's Instruments from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving Primary's Instruments from the database",
            )


InstrumentsServiceDependency = Annotated[InstrumentsService, Depends()]
