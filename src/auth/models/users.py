__all__ = ["LoginUser", "PublicStoredUser", "PrivateStoredUser"]

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, BaseModel, EmailStr, Field
from ...utils import PyObjectId


class Role(str, Enum):
    admin = "admin"
    user = "user"


class BaseUser(BaseModel):
    email: EmailStr


class LoginUser(BaseUser):
    password: str


class PublicStoredUser(BaseUser):
    role: Role
    deactivated_at: datetime | None = Field(default=None)
    id: PyObjectId = Field(validation_alias=AliasChoices("_id", "id"))

class PrivateStoredUser(PublicStoredUser):
    hash_password: str
