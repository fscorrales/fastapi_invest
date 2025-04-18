__all__ = ["ConnectPrimary"]

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --------------------------------------------------
class ConnectPrimary(BaseModel):
    server: Optional[str] = None
    date: datetime
    content_length: str
    connection: Optional[str] = None
    access_control_allow_credentials: str
    access_control_allow_methods: str
    access_control_allow_headers: str
    access_control_expose_headers: str
    x_auth_token: str
    cache_control: str
    pragma: str
    expires: str
    strict_transport_security: str
    x_xss_protection: str
    x_frame_options: str
    x_content_type_options: str
    set_cookie: str
