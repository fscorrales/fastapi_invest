#!/usr/bin/env python3
"""

Author  : Fernando Corrales <fscpython@gmail.com>

Date    : 18-abr-2025

Purpose : Connect to Primary API

API Docs: https://apihub.primary.com.ar/assets/apidoc/trading/index.html
"""

__all__ = ["get_token"]

import argparse
import asyncio
from datetime import datetime

import pytz
from httpx import AsyncClient
from tzlocal import get_localzone

from ..schemas import ConnectPrimary


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Connect to Primary API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Username for Primary's API access",
        metavar="username",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password for Primary's API access",
        metavar="password",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-l",
        "--live",
        help="Connect to Live Market Data",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-r",
        "--rest_url",
        help="URL for Primary's API Rest access",
        metavar="rest_url",
        type=str,
        default="https://api.remarkets.primary.com.ar",
    )

    parser.add_argument(
        "-ws",
        "--websocket",
        help="URL for Primary's API Websocket access",
        metavar="websocket_url",
        type=str,
        default="wss://api.remarkets.primary.com.ar",
    )

    args = parser.parse_args()

    if args.username is None or args.password is None:
        from ...config import settings

        args.username = (
            settings.PRIMARY_LIVE_USERNAME
            if args.live
            else settings.PRIMARY_REMARKETS_USERNAME
        )
        args.password = (
            settings.PRIMARY_LIVE_PASSWORD
            if args.live
            else settings.PRIMARY_REMARKETS_PASSWORD
        )
        if args.username is None or args.password is None:
            parser.error("Both --username and --password are required.")

    if args.live:
        args.rest_url = settings.PRIMARY_LIVE_URL
        args.websocket = settings.PRIMARY_LIVE_WS

    return args


# --------------------------------------------------
async def get_token(
    username: str,
    password: str,
    url: str,
    ws: str = None,
    httpxAsyncClient: AsyncClient = None,
) -> ConnectPrimary:
    token_url = url + "/auth/getToken"

    h = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Username": username,
        "X-Password": password,
    }

    if httpxAsyncClient:
        r = await httpxAsyncClient.post(token_url, headers=h)
    else:
        httpxAsyncClient = AsyncClient()
        try:
            r = await httpxAsyncClient.post(token_url, headers=h)
        finally:
            httpxAsyncClient.aclose()

    if r.status_code == 200:
        data = r.headers
        format_strptime = "%a, %d %b %Y %H:%M:%S %Z"

        # Parsear como UTC
        dt_utc = datetime.strptime(data["Date"], format_strptime)
        dt_utc = dt_utc.replace(tzinfo=pytz.utc)  # Asegurarse que está en UTC

        # Obtener la zona horaria del sistema
        local_tz = get_localzone()

        # Convertir
        dt_local = dt_utc.astimezone(local_tz)

        return ConnectPrimary(
            base_url=url,
            server=data.get("Server"),  # Usar get para evitar KeyError
            date=dt_local,
            content_length=data.get("Content-Length"),
            connection=data.get("Connection"),
            access_control_allow_credentials=data.get(
                "Access-Control-Allow-Credentials"
            ),
            access_control_allow_methods=data.get("Access-Control-Allow-Methods"),
            access_control_allow_headers=data.get("Access-Control-Allow-Headers"),
            access_control_expose_headers=data.get("Access-Control-Expose-Headers"),  # noqa: E501
            x_auth_token=data.get("X-Auth-Token"),
            cache_control=data.get("Cache-Control"),
            pragma=data.get("Pragma"),
            expires=data.get("Expires"),
            strict_transport_security=data.get("Strict-Transport-Security"),  # noqa: E501
            x_xss_protection=data.get("X-XSS-Protection"),
            x_frame_options=data.get("X-Frame-Options"),
            x_content_type_options=data.get("X-Content-Type-Options"),
            set_cookie=data.get("Set-Cookie"),
        )
    else:
        return None


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        print("Connecting to Primary API...")
        response = await get_token(
            username=args.username,
            password=args.password,
            token_url=args.rest_url,
            httpxAsyncClient=c,
        )
        print(response)
        print(f"Token {response.x_auth_token} expires at {response.expires}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.pyrofex.handlers.connect_primary
    # poetry run python -m src.pyrofex.handlers.connect_primary -l
