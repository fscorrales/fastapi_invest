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
import json
from typing import List

import websockets
from httpx import AsyncClient

from ..schemas import (
    ConnectPrimary,
    Entry,
    MarketData,
    MarketID,
    WSMessageSubscription,
    WSProductSubscription,
)
from .connect_primary import get_token

# Estado global del stream
stream_task = None


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
async def stream_market_data(
    primary: ConnectPrimary, msg_subscription: WSMessageSubscription, url: str = None
) -> List[MarketData]:
    """Get response from Primary WS API"""
    if url is None:
        url = primary.websocket_url

    h = {"X-Auth-Token": primary.x_auth_token}
    # h = [("X-Auth-Token", primary.x_auth_token)]
    msg_dict = msg_subscription.model_dump(mode="json")
    print(f"📡 Suscribiendo a {msg_dict}")

    async with websockets.connect(url, extra_headers=h) as ws:
        try:
            print("📡 Conectado a Primary API")
            await ws.send(json.dumps(msg_dict))
            # await ws.send(json.dumps(SUBSCRIPTION_MESSAGE))
            print("📡 Suscripción enviada a Primary")

            # Método 1
            # async for message in ws:
            #     await broadcast_message(message)

            # Método 2
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=10)
                    print("📥 Recibido:", message)
                except asyncio.TimeoutError:
                    print("⏳ No se recibió respuesta del servidor en 10 segundos.")
        except websockets.exceptions.ConnectionClosed:
            print("❌ Conexión cerrada por el servidor")
        except asyncio.CancelledError:
            print("🛑 Stream cancelado")
            raise
        finally:
            await ws.close()


# --------------------------------------------------
def start_stream(
    primary: ConnectPrimary, msg_subscription: WSMessageSubscription, url: str = None
):
    global stream_task
    if stream_task is None or stream_task.done():
        stream_task = asyncio.create_task(
            stream_market_data(primary=primary, msg_subscription=msg_subscription)
        )
        return True
    return False


# --------------------------------------------------
def stop_stream():
    global stream_task
    if stream_task and not stream_task.done():
        stream_task.cancel()
        return True
    return False


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()
    msg_subscription = WSMessageSubscription(
        entries=args.entries,
        products=[
            WSProductSubscription(
                symbol="MERV - XMEV - GGAL - 24hs",
                marketId="ROFX",
            )
        ],
    )

    print(json.dumps(msg_subscription.model_dump(mode="json")))
    print(f"Conectando a Primary API {args.websocket}")
    async with AsyncClient() as c:
        connect_primary = await get_token(
            username=args.username,
            password=args.password,
            url=args.rest_url,
            websocket_url=args.websocket,
            httpxAsyncClient=c,
        )
        try:
            start_stream(
                primary=connect_primary,
                msg_subscription=msg_subscription,
                url=args.websocket,
            )
        except Exception as e:
            print(f"Error al obtener instrumentos: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.primary.handlers.ws_market_data
    # poetry run python -m src.primary.handlers.ws_market_data
    # poetry run python -m src.primary.handlers.ws_market_data "MERV - XMEV - GGAL - 24hs" -l
