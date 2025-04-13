__all__ = ["UsersRepositoryDependency"]

from typing import Annotated

from fastapi import Depends

from ...config import BaseRepository
from ..schemas import PrivateStoredUser


class UsersRepository(BaseRepository[PrivateStoredUser]):
    collection_name = "users"
    model = PrivateStoredUser


UsersRepositoryDependency = Annotated[UsersRepository, Depends()]
