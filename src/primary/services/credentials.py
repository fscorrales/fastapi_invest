__all__ = ["prepare_primary_credentials"]

from ..schemas import Enviroment, PrimaryCredentials
from ...auth.services import OptionalAuthorizationDependency
from ...config import settings

def prepare_primary_credentials(
    auth: OptionalAuthorizationDependency,
    credentials: PrimaryCredentials,
) -> PrimaryCredentials:
    if auth.is_admin:
        credentials.username = (
            settings.PRIMARY_LIVE_USERNAME
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_USERNAME
        )
        credentials.password = (
            settings.PRIMARY_LIVE_PASSWORD
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_PASSWORD
        )
        credentials.url = (
            settings.PRIMARY_LIVE_URL
            if credentials.enviroment == Enviroment.live
            else settings.PRIMARY_REMARKETS_URL
        )
    return credentials