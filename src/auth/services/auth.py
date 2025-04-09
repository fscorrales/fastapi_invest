__all__ = [
    "Authentication",
    "AuthenticationDependency",
    "AuthorizationDependency",
]

from typing import Annotated

from fastapi import Depends, HTTPException, Response, Security, status
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from passlib.context import CryptContext

from ...config import JWT_SECRET, token_expiration_time
from ..models import LoginUser, PublicStoredUser

access_security = JwtAccessBearer(
    secret_key=JWT_SECRET,
    auto_error=True,
)

AuthCredentials = Annotated[JwtAuthorizationCredentials, Security(access_security)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authentication:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    def login_and_set_access_token(
        self, db_user: dict | None, user: LoginUser, response: Response
    ):
        if not db_user or not self.verify_password(
            user.password, db_user.get("hash_password")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or credentials incorrect",
            )

        userdata = PublicStoredUser.model_validate(db_user).model_dump()
        access_token = access_security.create_access_token(
            subject=userdata, expires_delta=token_expiration_time
        )
        access_security.set_access_cookie(response, access_token)

        return {"access_token": access_token}


class Authorization:
    def __init__(self, credentials: AuthCredentials):
        self.auth_user_id = credentials.subject.get("id")
        self.auth_user_name = credentials.subject.get("username")
        self.auth_user_role = credentials.subject.get("role")

    @property
    def is_admin(self):
        return self.auth_user_role == "admin"

    @property
    def is_user(self):
        return self.auth_user_role == "user"

    def is_admin_or_raise(self):
        if self.auth_user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not have admin role",
            )

AuthenticationDependency = Annotated[Authentication, Depends()]
AuthorizationDependency = Annotated[Authorization, Depends()]
