__all__ = ["auth_router"]

from fastapi import APIRouter, Response, Form

from typing import Annotated

from ..models import LoginUser
from ..services import (
    UsersServiceDependency,
    AuthenticationDependency,
    AuthorizationDependency,
)

from bson import ObjectId

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
def login_with_cookie(
    user: Annotated[LoginUser, Form()],
    response: Response,
    users: UsersServiceDependency,
    auth: AuthenticationDependency,
):
    db_user = users.get_one(username=user.username, with_password=True)
    return auth.login_and_set_access_token(
        user=user, db_user=db_user, response=response
    )


# @auth_router.get("/authenticated_user")
# def read_current_user(security: AuthorizationDependency, auth: AuthenticationDependency,):
#     return auth.get_current_user(id=ObjectId(security.auth_user_id))



@auth_router.post("/logout", include_in_schema=False)
def logout():
    pass