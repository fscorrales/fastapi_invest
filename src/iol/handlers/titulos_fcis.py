#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 26-mar-2025
Purpose: GET FCIs info from IOL
"""

__all__ = ["get_fcis"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient

from ..models import FCI, ConnectIOL
from .connect_iol import API_URL, get_token


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Get FCI's info from IOL",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Username for IOL's API access",
        metavar="username",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-p",
        "--password",
        help="Password for IOL's API access",
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
async def get_fcis(
    iol: ConnectIOL, url: str = None, httpxAsyncClient: AsyncClient = None
) -> FCI:
    """Get response from IOL"""
    # self.iol.update_token()
    if url is None:
        url = API_URL + "/api/v2/Titulos/FCI"

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
        # Extraer datos de cuentas y saldos
        fcis: List[FCI] = []

        for fci in data:
            fci_base = FCI(
                variacion=fci["variacion"],
                ultimoOperado=fci["ultimoOperado"],
                horizonteInversion=fci["horizonteInversion"],
                rescate=fci["rescate"],
                invierte=fci["invierte"],
                tipoFondo=fci["tipoFondo"],
                avisoHorarioEjecucion=fci["avisoHorarioEjecucion"],
                tipoAdministradoraTituloFCI=fci["tipoAdministradoraTituloFCI"],
                fechaCorte=fci["fechaCorte"],
                codigoBloomberg=fci["codigoBloomberg"],
                perfilInversor=fci["perfilInversor"],
                informeMensual=fci["informeMensual"],
                reglamentoGestion=fci["reglamentoGestion"],
                variacionMensual=fci["variacionMensual"],
                variacionAnual=fci["variacionAnual"],
                montoMinimo=fci["montoMinimo"],
                simbolo=fci["simbolo"],
                descripcion=fci["descripcion"],
                pais=fci["pais"],
                mercado=fci["mercado"],
                tipo=fci["tipo"],
                moneda=fci["moneda"],
            )
            fcis.append(fci_base)

        return fcis


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        connect_iol = await get_token(args.username, args.password, httpxAsyncClient=c)
        try:
            fcis = await get_fcis(iol=connect_iol, httpxAsyncClient=c)
            print(fcis)
        except Exception as e:
            print(f"Error al obtener estado de cuenta: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.iol.handlers.titulos_fcis
