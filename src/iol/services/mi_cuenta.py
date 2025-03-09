from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError

from ...config import COLLECTIONS, IOL_PASSWORD, IOL_USERNAME, db, logger
from ...utils import validate_and_extract_data_from_df
from ..handlers import get_estado_cuenta, get_token


class MiCuentaService:
    assert (collection_name := "users") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    def get_all_deleted(cls, query: FilterParamsUser) -> dict[str, list]:
        """Get all deleted users"""
        cursor = query.query_collection(cls.collection, get_deleted=True)
        return validate_and_extract_data(cursor, PublicStoredUser)


UsersServiceDependency = Annotated[MiCuentaService, Depends()]
