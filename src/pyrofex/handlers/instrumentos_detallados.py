#!/usr/bin/env python3
"""

Author  : Fernando Corrales <fscpython@gmail.com>

Date    : 19-abr-2025

Purpose : Lista de Instrumentos disponibles con más detalle

API Docs: https://apihub.primary.com.ar/assets/apidoc/trading/index.html#api-Instrumentos-detail
"""

__all__ = ["get_token"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient

from ..schemas import ConnectPrimary, InstrumentoDetallado
from .connect_primary import get_token


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

    return args


# --------------------------------------------------
async def get_instrumentos_detallados(
    primary: ConnectPrimary, url: str = None, httpxAsyncClient: AsyncClient = None
) -> List[InstrumentoDetallado]:
    """Get response from Primary REST API"""
    if url is None:
        url = primary.base_url + "/rest/instruments/details"

    h = {"X-Auth-Token": primary.x_auth_token}

    if httpxAsyncClient:
        r = await httpxAsyncClient.get(url, headers=h)
    else:
        httpxAsyncClient = AsyncClient()
        try:
            r = await httpxAsyncClient.get(url, headers=h)
        finally:
            httpxAsyncClient.aclose()

    if r.status_code == 200:
        data = r.json()
        # instrumentos = data
        enviroment = "REMARKETS" if "remarkets" in primary.base_url else "LIVE"
        instrumentos = [
            InstrumentoDetallado(
                symbol=instrumento["instrumentId"]["symbol"],
                marketId=instrumento["instrumentId"]["marketId"],
                marketSegmentId=instrumento["segment"]["marketSegmentId"],
                lowLimitPrice=instrumento["lowLimitPrice"],
                highLimitPrice=instrumento["highLimitPrice"],
                minPriceIncrement=instrumento["minPriceIncrement"],
                minTradeVol=instrumento["minTradeVol"],
                maxTradeVol=instrumento["maxTradeVol"],
                tickSize=instrumento["tickSize"],
                contractMultiplier=instrumento["contractMultiplier"],
                roundLot=instrumento["roundLot"],
                priceConvertionFactor=instrumento["priceConvertionFactor"],
                maturityDate=instrumento["maturityDate"],
                currency=instrumento["currency"],
                orderTypes=instrumento["orderTypes"],
                timesInForce=instrumento["timesInForce"],
                securityType=instrumento["securityType"],
                settlType=instrumento["settlType"],
                instrumentPricePrecision=instrumento["instrumentPricePrecision"],
                instrumentSizePrecision=instrumento["instrumentSizePrecision"],
                securityId=instrumento["securityId"],
                securityIdSource=instrumento["securityIdSource"],
                securityDescription=instrumento["securityDescription"],
                tickPriceRanges=instrumento["tickPriceRanges"],
                strike=instrumento["strike"],
                underlying=instrumento["underlying"],
                cficode=instrumento["cficode"],
                enviroment=enviroment,
            )
            for instrumento in data["instruments"]
        ]

        return instrumentos


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        connect_primary = await get_token(
            username=args.username,
            password=args.password,
            url=args.rest_url,
            httpxAsyncClient=c,
        )
        try:
            instrumentos = await get_instrumentos_detallados(
                primary=connect_primary, httpxAsyncClient=c
            )
            print(instrumentos)
        except Exception as e:
            print(f"Error al obtener instrumentos: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.pyrofex.handlers.instrumentos_detallados
    # poetry run python -m src.pyrofex.handlers.instrumentos_detallados -l
