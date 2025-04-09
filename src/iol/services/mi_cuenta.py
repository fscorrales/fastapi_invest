__all__ = ["MiCuentaServiceDependency"]

from typing import Annotated

from fastapi import Depends, HTTPException
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import COLLECTIONS, Database, logger
from ..handlers import get_estado_cuenta, get_token
from ..schemas import EstadoCuenta


class MiCuentaService:
    collection_name = "iol_mi_cuenta_estado"
    collection = None

    @classmethod
    def init_collection(cls):
        assert cls.collection_name in COLLECTIONS
        cls.collection = Database.db[cls.collection_name]

    @classmethod
    async def get_mi_cuenta_estado(cls, username: str, password: str) -> EstadoCuenta:
        async with AsyncClient() as c:
            try:
                # Intentar obtener el token
                connect_iol = await get_token(username, password, httpxAsyncClient=c)
                # Intentar obtener el estado de cuenta
                estado_cuenta = await get_estado_cuenta(
                    iol=connect_iol, httpxAsyncClient=c
                )
                return estado_cuenta
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


MiCuentaServiceDependency = Annotated[MiCuentaService, Depends()]
