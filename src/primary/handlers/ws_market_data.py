#!/usr/bin/env python3
"""

Author  : Fernando Corrales <fscpython@gmail.com>

Date    : 20-abr-2025

Purpose : Obtener datos actuales de instrumentos del mercado.

API Docs: https://apihub.primary.com.ar/assets/apidoc/trading/index.html#api-Precios-get
"""

__all__ = ["format_params", "stream_market_data"]

import argparse
import asyncio
from typing import List

import orjson
import websockets
from httpx import AsyncClient

from ..schemas import (
    ConnectPrimary,
    Entry,
    MarketData,
    MarketID,
    SettlementTerm,
    WSMarketDataParams,
    WSProductSubscription,
)
from ..services.format import format_instruments
from .connect_primary import get_token

# Estado global del stream
stream_task = None
# Cola compartida
message_queue = asyncio.Queue()


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Connect to Primary API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "symbols",
        help="Specify one or more symbols of the instruments to look up (e.g., GGAL YPFD PAMP)",
        metavar="Symbols",
        type=str,
        nargs="+",
    )

    parser.add_argument(
        "-t",
        "--terms",
        help="Settlement terms for the trade (e.g., 24hs 48hs CI)",
        metavar="term",
        type=str,
        choices=[c.value for c in SettlementTerm],
        default=["CI", "24hs"],
        nargs="+",
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
        default=["LA", "HI", "LO", "BI", "OF", "NV", "EV"],
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

    return args


# --------------------------------------------------
async def receive_messages(ws):
    while True:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            print("📥 Mensaje recibido:", raw)
            await message_queue.put(raw)
        except asyncio.TimeoutError:
            print("⏳ Timeout...")
        except websockets.exceptions.ConnectionClosed:
            print("❌ Conexión cerrada por el servidor")
        except asyncio.CancelledError:
            print("🛑 Stream cancelado")
            raise


# --------------------------------------------------
async def process_messages():
    while True:
        raw = await message_queue.get()
        try:
            msg = orjson.loads(raw)
            if msg.get("type") == "Md":
                # Ejemplo: parseo manual y simple
                instrument = msg["instrumentId"]["symbol"]
                price = msg["marketData"].get("OP")
                print(f"💰 {instrument}: {price}")
                # Guardar en Mongo, convertir a DataFrame, etc.

        except Exception as e:
            print(f"⚠️ Error procesando mensaje: {e}")
        finally:
            message_queue.task_done()


# --------------------------------------------------
def format_params(params: WSMarketDataParams) -> WSMarketDataParams:
    """Format parameters for the subscription message"""
    formatted_instruments = format_instruments(
        symbols=params.symbols, settlement_terms=params.settlement_terms
    )
    # params.products = [
    #     WSProductSubscription(symbol=s, marketId=params.marketId)
    #     for s in formatted_instruments
    # ]
    # params.settlement_terms = None
    # params.symbols = None
    # params.marketId = None
    # return params
    return {
        "type": "smd",
        "level": 1,
        "entries": params.entries,
        "products": [
            WSProductSubscription(symbol=s, marketId=params.marketId).model_dump()
            for s in formatted_instruments
        ],
        "depth": params.depth,
    }


# --------------------------------------------------
async def stream_market_data(
    primary: ConnectPrimary,
    params: WSMarketDataParams,
    url: str = None,
    # seconds_delay: int = 5,
) -> List[MarketData]:
    """Get response from Primary WS API"""
    if url is None:
        url = primary.websocket_url

    h = {"X-Auth-Token": primary.x_auth_token}

    # Params para el mensaje de suscripción
    msg_dict = format_params(params)
    # msg_dict = params.model_dump(mode="json", exclude_none=True)
    print(f"📡 Suscribiendo a {msg_dict}")

    async with websockets.connect(url, extra_headers=h) as ws:
        # Método 2
        # try:
        #     print("📡 Conectado a Primary API")
        #     await ws.send(json.dumps(msg_dict))
        #     print("📡 Suscripción enviada a Primary")

        #     # Método 1
        #     # async for message in ws:
        #     #     await broadcast_message(message)

        #
        #     while True:
        #         try:
        #             message = await asyncio.wait_for(ws.recv(), timeout=10)
        #             print("📥 Recibido:", message)
        #         except asyncio.TimeoutError:
        #             print("⏳ No se recibió respuesta del servidor en 10 segundos.")

        # except websockets.exceptions.ConnectionClosed:
        #     print("❌ Conexión cerrada por el servidor")
        # except asyncio.CancelledError:
        #     print("🛑 Stream cancelado")
        #     raise
        # finally:
        #     await ws.close()

        # Método 3
        print("📡 Conectado a Primary")
        await ws.send(orjson.dumps(msg_dict).decode())

        # Ejecutamos recepción y procesamiento en paralelo
        consumer = asyncio.create_task(process_messages())
        producer = asyncio.create_task(receive_messages(ws))

        await asyncio.gather(producer, consumer)


# # --------------------------------------------------
# def start_stream(primary: ConnectPrimary, params: WSMarketDataParams):
#     global stream_task
#     if stream_task is None or stream_task.done():
#         stream_task = asyncio.create_task(
#             stream_market_data(primary=primary, params=params)
#         )
#         return True
#     return False


# # --------------------------------------------------
# def stop_stream():
#     global stream_task
#     if stream_task and not stream_task.done():
#         stream_task.cancel()
#         return True
#     return False


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    msg_subscription = WSMarketDataParams(
        symbols=args.symbols,
        settlement_terms=args.terms,
        marketId=args.market_id,
        entries=args.entries,
        depth=args.depth,
    )

    async with AsyncClient() as c:
        connect_primary = await get_token(
            username=args.username,
            password=args.password,
            url=args.rest_url,
            websocket_url=args.websocket,
            httpxAsyncClient=c,
        )
        try:
            await stream_market_data(
                primary=connect_primary,
                params=msg_subscription,
            )
        except Exception as e:
            print(f"Error al obtener instrumentos: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest
    # python -m src.primary.handlers.ws_market_data
    # poetry run python -m src.primary.handlers.ws_market_data
    # poetry run python -m src.primary.handlers.ws_market_data GGAL TXAR -l -d 3
