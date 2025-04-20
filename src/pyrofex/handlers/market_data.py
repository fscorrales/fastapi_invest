#!/usr/bin/env python3
"""

Author  : Fernando Corrales <fscpython@gmail.com>

Date    : 20-abr-2025

Purpose : Obtener datos actuales de instrumentos del mercado.

API Docs: https://apihub.primary.com.ar/assets/apidoc/trading/index.html#api-Precios-get
"""

__all__ = ["get_token"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient

from ..schemas import ConnectPrimary, Entry, MarketData, MarketID, ParamsMarketData
from .connect_primary import get_token


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Connect to Primary API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "symbol",
        help="Specify the symbol of the instrument to look up (e.g., GGAL, YPFD)",
        metavar="symbol",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-m",
        "--market_id",
        metavar="market_id",
        help="Specify the market id to look up (e.g., ROFX, MERV)",
        default="ROFX",
        type=str,
        choices=[c.value for c in MarketID],
    )

    parser.add_argument(
        "-e",
        "--entries",
        help="Instrument entries to look up (e.g., BI, OF, LA)",
        metavar="entries",
        type=str,
        nargs="+",
        default=["OP", "CL", "HI", "LO", "TV"],
        choices=[c.value for c in Entry],
    )

    parser.add_argument(
        "-d",
        "--depth",
        help="Market depth (default: 1)",
        metavar="depth",
        type=int,
        default=1,
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
        default="https://api.remarkets.primary.com.ar/",
    )

    parser.add_argument(
        "-ws",
        "--websocket",
        help="URL for Primary's API Websocket access",
        metavar="websocket_url",
        type=str,
        default="wss://api.remarkets.primary.com.ar/",
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

    args.environment = "LIVE" if args.live else "REMARKETS"
    args.external = False if args.market_id == MarketID.rofex.value else True

    return args


# --------------------------------------------------
async def get_market_hist_data(
    primary: ConnectPrimary,
    params: ParamsMarketData,
    url: str = None,
    httpxAsyncClient: AsyncClient = None,
) -> List[MarketData]:
    """Get response from Primary REST API"""
    if url is None:
        url = primary.base_url + "/rest/marketdata/get"

    h = {"X-Auth-Token": primary.x_auth_token}
    params_dict = params.model_dump(mode="json")

    if httpxAsyncClient:
        r = await httpxAsyncClient.get(url, headers=h, params=params_dict)
    else:
        httpxAsyncClient = AsyncClient()
        try:
            r = await httpxAsyncClient.get(url, headers=h, params=params_dict)
        finally:
            httpxAsyncClient.aclose()

    if r.status_code == 200:
        data = r.json()
        instrumentos = data
        # if data["status"] == "OK":
        #     enviroment = "REMARKETS" if "remarkets" in primary.base_url else "LIVE"
        #     # Verificar si data[data_field] es un diccionario o una lista
        #     if isinstance(data["instruments"], dict):
        #         # Si es un diccionario, conviértelo en una lista con un solo elemento
        #         instrumentos_data = [data["instruments"]]
        #     else:
        #         # Si es una lista, úsala directamente
        #         instrumentos_data = data["instruments"]
        #     instrumentos = [
        #         MarketHistData(
        #             symbol=instrumento["symbol"],
        #             marketId=instrumento["marketId"],
        #             enviroment=enviroment,
        #         )
        #         for instrumento in instrumentos_data
        #     ]
        # else:
        #     raise ValueError(f"Primary API Error: {data.get('description')}")
        return instrumentos


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()
    params = ParamsMarketData(
        marketId=args.market_id,
        symbol=args.symbol,
        depth=args.depth,
        entries=args.entries,
    )

    async with AsyncClient() as c:
        connect_primary = await get_token(
            username=args.username,
            password=args.password,
            url=args.rest_url,
            httpxAsyncClient=c,
        )
        try:
            print("params", params.model_dump(mode="json"))
            data = await get_market_hist_data(
                primary=connect_primary, httpxAsyncClient=c, params=params
            )
            print(data)
        except Exception as e:
            print(f"Error al obtener instrumentos: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.pyrofex.handlers.market_data 'DLR/DIC23'
    # poetry run python -m src.pyrofex.handlers.market_data 'MERV - XMEV - GGAL - 24hs'
    # poetry run python -m src.pyrofex.handlers.market_data 'MERV - XMEV - GGAL - 24hs' -l
