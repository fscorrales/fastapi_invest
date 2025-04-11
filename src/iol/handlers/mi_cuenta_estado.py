#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 08-mar-2025
Purpose: GET estado de cuenta IOL
"""

__all__ = ["get_estado_cuenta"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient

from ..schemas import ConnectIOL, Cuenta, MiCuentaEstado, SaldoCuenta
from .connect_iol import API_URL, get_token


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Read, process and write SIIF's rf602",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        from ...config import IOL_PASSWORD, IOL_USERNAME

        args.username = IOL_USERNAME
        args.password = IOL_PASSWORD
        if args.username is None or args.password is None:
            parser.error("Both --username and --password are required.")

    return args


# --------------------------------------------------
async def get_estado_cuenta(
    iol: ConnectIOL, url: str = None, httpxAsyncClient: AsyncClient = None
) -> MiCuentaEstado:
    """Get response from IOL"""
    # self.iol.update_token()
    if url is None:
        url = API_URL + "/api/v2/estadocuenta"

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
        cuentas_data: List[Cuenta] = []
        saldos_data: List[SaldoCuenta] = []

        for cuenta in data["cuentas"]:
            cuenta_base = Cuenta(
                numero=cuenta["numero"],
                tipo=cuenta["tipo"],
                moneda=cuenta["moneda"],
                disponible=cuenta["disponible"],
                comprometido=cuenta["comprometido"],
                saldo=cuenta["saldo"],
                titulosValorizados=cuenta["titulosValorizados"],
                total=cuenta["total"],
                margenDescubierto=cuenta["margenDescubierto"],
                estado=cuenta["estado"],
            )
            cuentas_data.append(cuenta_base)

            for saldo in cuenta["saldos"]:
                saldos_data.append(
                    SaldoCuenta(
                        numero=cuenta_base.numero,
                        tipo=cuenta_base.tipo,
                        moneda=cuenta_base.moneda,
                        liquidacion=saldo["liquidacion"],
                        saldo=saldo["saldo"],
                        comprometido=saldo["comprometido"],
                        disponible=saldo["disponible"],
                        disponibleOperar=saldo["disponibleOperar"],
                    )
                )

        return MiCuentaEstado(
            cuentas=cuentas_data,
            saldos=saldos_data,
        )


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    async with AsyncClient() as c:
        connect_iol = await get_token(args.username, args.password, httpxAsyncClient=c)
        try:
            estado_cuenta = await get_estado_cuenta(iol=connect_iol, httpxAsyncClient=c)
            print(estado_cuenta)
        except Exception as e:
            print(f"Error al obtener estado de cuenta: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.iol.handlers.mi_cuenta_estado
