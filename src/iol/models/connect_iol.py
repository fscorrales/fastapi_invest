__all__ = ["ConnectIOL"]

from datetime import datetime

from pydantic import BaseModel


# --------------------------------------------------
class ConnectIOL(BaseModel):
    access_token: str
    expires_utc: datetime
    refresh_token: str
    refresh_expires_utc: datetime
