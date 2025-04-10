from typing import Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ...config import COLLECTIONS, Database

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    collection_name: str
    model: Type[ModelType]
    unique_field: Optional[str] = None

    def __init__(self):
        if not hasattr(self, "collection_name") or not hasattr(self, "model"):
            raise NotImplementedError("Repos must define 'collection_name' and 'model'")
        if self.collection_name not in COLLECTIONS:
            raise ValueError(f"'{self.collection_name}' not found in COLLECTIONS")

        self.collection = Database.db[self.collection_name]  # Motor async collection

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

        await self.collection.insert_one(doc)
        return data

    async def get_all(self, limit: int = 100) -> List[ModelType]:
        docs = await self.collection.find().to_list(length=limit)
        return [self.model(**doc) for doc in docs]

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": id})
        return self.model(**doc) if doc else None

    async def delete_by_id(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count == 1

    async def get_paginated(self, skip: int = 0, limit: int = 20) -> List[ModelType]:
        cursor = self.collection.find().skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in docs]
