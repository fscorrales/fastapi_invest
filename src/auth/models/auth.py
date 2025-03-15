__all__ = ["LoginUser", "PublicStoredUser"]

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, BaseModel, EmailStr, Field
from pydantic_mongo import PydanticObjectId


class Role(str, Enum):
    admin = "admin"
    user = "user"


class BaseUser(BaseModel):
    username: str
    email: EmailStr


class LoginUser(BaseModel):
    username: str
    password: str


class PublicStoredUser(BaseUser):
    role: Role
    deactivated_at: datetime | None = Field(default=None)
    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))
