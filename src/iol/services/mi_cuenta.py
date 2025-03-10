__all__ = ["MiCuentaServiceDependency"]

from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from pydantic import ValidationError

from ...config import COLLECTIONS, IOL_PASSWORD, IOL_USERNAME, db, logger
from ...utils import validate_and_extract_data_from_df
from ..handlers import get_estado_cuenta, get_token
from ..models import EstadoCuentaValidationOutput, SaldoCuenta


class MiCuentaService:
    assert (collection_name := "iol_mi_cuenta_estado") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    async def get_mi_cuenta_estado(cls) -> EstadoCuentaValidationOutput:
        async with AsyncClient() as c:
            connect_iol = await get_token(
                IOL_USERNAME, IOL_PASSWORD, httpxAsyncClient=c
            )
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
