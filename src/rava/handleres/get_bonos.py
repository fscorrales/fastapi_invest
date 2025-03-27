#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 27-mar-2025
Purpose: GET Bonos from RAVA internal API
"""

__all__ = ["get_bonos"]

import argparse
import asyncio
from typing import List

from httpx import AsyncClient


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Get FCI's info from IOL",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
async def get_bonos(url: str = None, httpxAsyncClient: AsyncClient = None):

    if url is None:
        url = "https://www.rava.com/perfil/ajax/get_panel_bonos.php"

    if httpxAsyncClient:
        r = await httpxAsyncClient.get(url)
    else:
        httpxAsyncClient = AsyncClient()
        try:
            r = await httpxAsyncClient.get(url)
        finally:
            httpxAsyncClient.aclose()

    return r.json() if r.status_code == 200 else None

    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url)
    #     return response.json() if response.status_code == 200 else None

async def obtener_bonos():
    url = "https://www.rava.com/perfil/ajax/get_panel_bonos.php"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.rava.com/cotizaciones/bonos",
    }

    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Contenido: {response.text[:500]}")

        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print(f"Error al convertir a JSON: {e}")
                return None
        else:
            print("La API de Rava no respondió correctamente.")
            return None


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()

    # async with AsyncClient() as c:
    #     try:
    #         bonos = await get_bonos(httpxAsyncClient=c)
    #         print(bonos)
    #     except Exception as e:
    #         print(f"Error al obtener listado de bonos desde Rava: {e}")

    bonos = await obtener_bonos()
    print(bonos)


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.rava.handleres.get_bonos
