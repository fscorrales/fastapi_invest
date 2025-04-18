#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gmail.com>
Date   : 08-mar-2025
Purpose: GET portafolio de cuenta IOL
"""

__all__ = ["get_portafolio"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient

from ..schemas import ConnectIOL, Pais, PosicionPortafolio
from .connect_iol import API_URL, get_token


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Read, process and write SIIF's rf602",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "pais",
        metavar="pais",
        help="Country name (estados_Unidos or argentina)",
        type=str,
        choices=["estados_Unidos", "argentina"],
        default="argentina",
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Username for SIIF access",
        metavar="username",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password for SIIF access",
        metavar="password",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    if args.username is None or args.password is None:
        from ...config import settings

        args.username = settings.IOL_USERNAME
        args.password = settings.IOL_PASSWORD
        if args.username is None or args.password is None:
            parser.error("Both --username and --password are required.")

    return args


# --------------------------------------------------
async def get_portafolio(
    iol: ConnectIOL, pais: Pais, url: str = None, httpxAsyncClient: AsyncClient = None
) -> List[PosicionPortafolio]:
    """Get response from IOL"""
    # self.iol.update_token()
    if url is None:
        url = API_URL + "/api/v2/portafolio/" + pais

    h = {"Authorization": "Bearer " + iol.access_token}

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
        pais = data["pais"]
        posicion_portofolio: List[PosicionPortafolio] = []

        for posicion in data["activos"]:
            posicion_base = PosicionPortafolio(
                pais=pais,
                cantidad=posicion["cantidad"],
                comprometido=posicion["comprometido"],
                puntosVariacion=posicion["puntosVariacion"],
                variacionDiaria=posicion["variacionDiaria"],
                ultimoPrecio=posicion["ultimoPrecio"],
                ppc=posicion["ppc"],
                gananciaPorcentaje=posicion["gananciaPorcentaje"],
                gananciaDinero=posicion["gananciaDinero"],
                valorizado=posicion["valorizado"],
                titulo=posicion["titulo"],
                parking=posicion["parking"],
            )
            posicion_portofolio.append(posicion_base)

        return posicion_portofolio


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        connect_iol = await get_token(args.username, args.password, httpxAsyncClient=c)
        try:
            portafolio = await get_portafolio(
                iol=connect_iol, pais=args.pais, httpxAsyncClient=c
            )
            print(portafolio)
        except Exception as e:
            print(f"Error al obtener portafolio: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.iol.handlers.mi_cuenta_portafolio argentina
