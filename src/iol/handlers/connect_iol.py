#!/usr/bin/env python3
"""

Author  : Fernando Corrales <fscpython@gamail.com>

Date    : 08-mar-2025

Purpose : Connect to IOL

API Docs: https://api.invertironline.com/
"""

__all__ = ["get_token", "API_URL"]

import argparse
import asyncio
from datetime import datetime

from httpx import AsyncClient

from ..schemas import ConnectIOL

API_URL = "https://api.invertironline.com"


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Connect to IOL",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Username for IOL access",
        metavar="username",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password for IOL access",
        metavar="password",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    if args.username is None or args.password is None:
        from ...config import IOL_PASSWORD, IOL_USERNAME

        args.username = IOL_USERNAME
        args.password = IOL_PASSWORD
        if args.username is None or args.password is None:
            parser.error("Both --username and --password are required.")

    return args


# --------------------------------------------------
async def get_token(
    username: str, password: str, url: str = None, httpxAsyncClient: AsyncClient = None
) -> ConnectIOL:
    if url is None:
        url = API_URL + "/token"

    h = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    if httpxAsyncClient:
        r = await httpxAsyncClient.post(url, headers=h, data=body)
    else:
        httpxAsyncClient = AsyncClient()
        try:
            r = await httpxAsyncClient.post(url, headers=h, data=body)
        finally:
            httpxAsyncClient.aclose()

    if r.status_code == 200:
        data = r.json()
        format_strptime = "%a, %d %b %Y %H:%M:%S %Z"
        return ConnectIOL(
            access_token=data["access_token"],
            expires_utc=datetime.strptime(data[".expires"], format_strptime),
            refresh_token=data["refresh_token"],
            refresh_expires_utc=datetime.strptime(
                data[".refreshexpires"], format_strptime
            ),
        )
    else:
        return None


# --------------------------------------------------
async def update_token(connect_iol: ConnectIOL):
    pass
    # # Time to expire
    # expire = dt.datetime.strptime(self.token[".expires"], "%a, %d %b %Y %H:%M:%S GMT")
    # now = dt.datetime.utcnow()
    # diff_time = expire - now
    # days = diff_time.days

    # if days == 0:
    #     return self.token
    # else:
    #     self.get_token()
    #     print(f"Token has been updated. Expires in {self.token['.expires']}")


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        response = await get_token(
            username=args.username, password=args.password, httpxAsyncClient=c
        )
        print(response)


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.iol.handlers.connect_iol
