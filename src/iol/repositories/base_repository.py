from typing import TypeVar, Generic, Type, Optional
from pydantic import BaseModel
from ...config import Database, COLLECTIONS

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    collection_name: str
    model: Type[ModelType]

    def __init__(self):
        if not hasattr(self, "collection_name") or not hasattr(self, "model"):
            raise NotImplementedError("Repos must define 'collection_name' and 'model'")
        if self.collection_name not in COLLECTIONS:
            raise ValueError(f"'{self.collection_name}' not found in COLLECTIONS")
        self.collection = Database.db[self.collection_name]

    async def save(self, data: ModelType):
        """Guarda un documento validado"""
        doc = data.model_dump(by_alias=True)
        return await self.collection.insert_one(doc)

    async def get_all(self, limit: int = 100) -> list[ModelType]:
        result = await self.collection.find().to_list(length=limit)
        return [self.model(**doc) for doc in result]

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.model(**doc)
        return None