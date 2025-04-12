__all__ = ["TitulosServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import get_fcis, get_token
from ..repositories import (
    TitulosFCIsRepositoryDependency,
)
from ..schemas import FCI


# -------------------------------------------------
@dataclass
class TitulosService:
    fcis: TitulosFCIsRepositoryDependency

    # -------------------------------------------------
    async def sync_fcis_from_iol(self, username: str, password: str) -> List[FCI]:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_iol = await get_token(username, password, httpxAsyncClient=c)
                # Intentar obtener el estado de cuenta
                fcis = await get_fcis(iol=connect_iol, httpxAsyncClient=c)

                fcis_to_store = [FCI(**fci.model_dump()) for fci in fcis]

                await self.fcis.delete_all()
                await self.fcis.save_all(fcis_to_store)

                return fcis
            except ValidationError as e:
                logger.error(f"Validation Error: {e}")
                raise HTTPException(
                    status_code=400, detail="Invalid response format from IOL"
                )
            except Exception as e:
                logger.error(f"Error during report processing: {e}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials or unable to authenticate",
                )

    # -------------------------------------------------
    async def get_fcis_from_db(self) -> List[FCI]:
        try:
            fcis = await self.fcis.get_all()
            return fcis
        except Exception as e:
            logger.error(f"Error retrieving FCIs from database: {e}")
            raise HTTPException(
                status_code=500, detail="Error retrieving FCIs from the database"
            )


TitulosServiceDependency = Annotated[TitulosService, Depends()]
