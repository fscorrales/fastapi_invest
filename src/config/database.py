__all__ = ["Database", "COLLECTIONS", "BaseRepository"]

from typing import Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from .__base_config import settings
from ..utils import BaseFilterParams

ModelType = TypeVar("ModelType", bound=BaseModel)

MONGO_DB_NAME = "invest"
COLLECTIONS = [
    "users",
    "iol_mi_cuenta_cuentas",
    "iol_mi_cuenta_saldos",
    "iol_mi_cuenta_portafolio",
    "iol_titulos_fcis",
    "primary_segments",
    "primary_instruments",
    "primary_instruments_details",
]


# -------------------------------------------------
class Database:
    client = None
    db = None

    @classmethod
    def initialize(cls):
        cls.client = AsyncIOMotorClient(settings.DB_URI)
        cls.db = cls.client[MONGO_DB_NAME]


# -------------------------------------------------
class BaseRepository(Generic[ModelType]):
    collection_name: str
    model: Type[ModelType]
    unique_field: Optional[str] = None

    # -------------------------------------------------
    def __init__(self):
        if not hasattr(self, "collection_name") or not hasattr(self, "model"):
            raise NotImplementedError("Repos must define 'collection_name' and 'model'")
        if self.collection_name not in COLLECTIONS:
            raise ValueError(f"'{self.collection_name}' not found in COLLECTIONS")

        self.collection = Database.db[self.collection_name]  # Motor async collection

    # -------------------------------------------------
    async def save(self, data: ModelType) -> ModelType:
        doc = jsonable_encoder(data, by_alias=True)

        if self.unique_field and doc.get(self.unique_field):
            existing = await self.collection.find_one(
                {self.unique_field: doc[self.unique_field]}
            )
            if existing:
                raise ValueError(
                    f"Duplicate entry for field '{self.unique_field}': {doc[self.unique_field]}"
                )

        return await self.collection.insert_one(doc)

    # -------------------------------------------------
    async def save_all(self, data: List[ModelType]) -> List[ModelType]:
        if isinstance(data, list):
            data = [jsonable_encoder(doc, by_alias=True) for doc in data]
        else:
            data = jsonable_encoder(data, by_alias=True)
        return await self.collection.insert_many(data)

    # -------------------------------------------------
    async def get_all(self, limit: int = 100) -> List[ModelType]:
        return await self.collection.find().to_list(length=limit)
        # return [self.model(**doc) for doc in docs]

    # -------------------------------------------------
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": id})
        return doc if doc else None

    # -------------------------------------------------
    async def get_by_fields(self, fields: dict) -> Optional[ModelType]:
        """
        Find a document by one or more fields.

        Args:
            fields (dict): A dictionary where keys are field names and values are the values to match.

        Returns:
            Optional[ModelType]: The document that matches the fields, or None if not found.
        """
        if not fields:
            raise ValueError("Fields dictionary cannot be empty")

        doc = await self.collection.find_one(fields)
        return doc if doc else None

    # -------------------------------------------------
    async def get_by_fields_or(self, fields: dict) -> Optional[ModelType]:
        """
        Find a document by multiple fields using an $or filter.

        Args:
            fields (dict): A dictionary where keys are field names and values are the values to match.

        Returns:
            Optional[ModelType]: The document that matches the filter, or None if not found.
        """
        if not fields:
            raise ValueError("Fields dictionary cannot be empty")

        # Construir el filtro $or dinámicamente
        filter = {"$or": [{key: value} for key, value in fields.items()]}

        # Buscar el documento en la base de datos
        doc = await self.collection.find_one(filter)
        return doc if doc else None

    # -------------------------------------------------
    async def delete_by_id(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    # -------------------------------------------------
    async def delete_by_fields(self, fields: dict) -> int:
        """
        Delete documents based on multiple fields (AND logic).

        Args:
            fields (dict): A dictionary where keys are field names and values are the values to match.

        Returns:
            int: The number of documents deleted.
        """
        if not fields:
            raise ValueError("Fields dictionary cannot be empty")

        # Construir el filtro basado en los campos proporcionados
        filter = {key: value for key, value in fields.items()}

        # Eliminar los documentos que coincidan con el filtro
        result = await self.collection.delete_many(filter)
        return result.deleted_count

    # -------------------------------------------------
    async def delete_all(self) -> int:
        result = await self.collection.delete_many({})
        return result.deleted_count

    # -------------------------------------------------
    async def get_paginated(self, skip: int = 0, limit: int = 20) -> List[ModelType]:
        cursor = self.collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in docs]

    # -------------------------------------------------
    async def find_with_filter_params(self, params: BaseFilterParams) -> list[ModelType]:
        filter_dict = params.get_full_filter()
        sort_direction = 1 if params.sort_dir == "asc" else -1

        cursor = (
            self.collection.find(filter_dict)
            .skip(params.offset)
            .limit(params.limit)
            .sort(params.sort_by, sort_direction)
        )
        return await cursor.to_list(length=params.limit)
        # return [self.model(**doc) for doc in docs]