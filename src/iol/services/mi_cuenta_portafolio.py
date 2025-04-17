__all__ = ["MiCuentaPortafolioServiceDependency"]

from dataclasses import dataclass
from typing import Annotated, List

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import logger
from ..handlers import get_portafolio, get_token
from ..repositories import (
    MiCuentaPortafolioRepositoryDependency,
)
from ..schemas import PosicionPortafolio, StoredPosicionPortafolio


# -------------------------------------------------
@dataclass
class MiCuentaPortafolioService:
    portafolio: MiCuentaPortafolioRepositoryDependency

    # -------------------------------------------------
    async def sync_portafolio_from_iol(
        self, username: str, password: str, pais: str = "argentina"
    ) -> List[PosicionPortafolio]:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_iol = await get_token(username, password, httpxAsyncClient=c)
                # Intentar obtener el estado de cuenta
                portafolio_to_store = await get_portafolio(
                    iol=connect_iol, pais=pais, httpxAsyncClient=c
                )

                # portafolio_to_store = [
                #     PosicionPortafolio(**cuenta.model_dump()) for cuenta in portafolio
                # ]
                await self.portafolio.delete_by_fields(
                    {"pais": pais}
                )  # Eliminar el portafolio anterior
                await self.portafolio.save_all(portafolio_to_store)

                return portafolio_to_store
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
    async def get_portafolio_from_db(self) -> List[StoredPosicionPortafolio]:
        try:
            return await self.portafolio.get_all()
        except Exception as e:
            logger.error(f"Error retrieving IOL'S Portafolio from database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error retrieving IOL'S Portafolio from the database",
            )


MiCuentaPortafolioServiceDependency = Annotated[MiCuentaPortafolioService, Depends()]
