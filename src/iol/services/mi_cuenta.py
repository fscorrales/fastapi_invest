__all__ = ["MiCuentaServiceDependency"]

from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import COLLECTIONS, Database, logger
from ...utils import validate_and_extract_data_from_df
from ..handlers import get_estado_cuenta, get_token
from ..schemas import EstadoCuentaValidationOutput, SaldoCuenta


class MiCuentaService:
    collection_name = "users"
    collection = None

    @classmethod
    def init_collection(cls):
        assert cls.collection_name in COLLECTIONS
        cls.collection = Database.db[cls.collection_name]

    @classmethod
    async def get_mi_cuenta_estado(
        cls, username: str, password: str
    ) -> EstadoCuentaValidationOutput:
        cls.init_collection()
        async with AsyncClient() as c:
            connect_iol = await get_token(username, password, httpxAsyncClient=c)
            try:
                estado_cuenta = await get_estado_cuenta(
                    iol=connect_iol, httpxAsyncClient=c
                )
                return estado_cuenta
                # return validate_and_extract_data_from_df(
                #     estado_cuenta.saldos, SaldoCuenta
                # )
            except ValidationError as e:
                logger.error(f"Validation Error: {e}")
            except Exception as e:
                logger.error(f"Error during report processing: {e}")


MiCuentaServiceDependency = Annotated[MiCuentaService, Depends()]
