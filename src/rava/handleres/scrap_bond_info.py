#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gmail.com>
Date   : 27-mar-2025
Purpose: Scrap Bonds from RAVA
"""

__all__ = ["ScrapRavaBondInfo"]

import argparse
import asyncio
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from ...utils import parse_date, to_float
from ..schemas import RavaBondCashFlow, RavaBondProfile
from .connect import RavaManager, connect_rava


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Scrap Bonds from RAVA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--symbol",
        help="Rava's bond symbol",
        metavar="str",
        type=str,
        default="AL30",
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
@dataclass
class ScrapRavaBondInfo(RavaManager):
    # --------------------------------------------------
    async def get_rendered_html(self, symbol: str = None, url: str = None) -> str:
        """Get the rendered HTML of the RAVA bonds page using Playwright"""
        if symbol is not None:
            url = f"https://www.rava.com/perfil/{symbol}"
        elif url is None:
            url = "https://www.rava.com/perfil/AL30"

        if self.rava.url != url:
            await self.rava.page.goto(url)  # timeout=30000
            await self.rava.page.wait_for_load_state("networkidle")
            self.rava.url = url

        # Wait for the bonds table to appear (adjust selector if necessary)
        await self.rava.page.wait_for_selector(
            "table", timeout=15000
        )  # Wait 15 seconds

        # Get the rendered HTML
        self.rendered_html = await self.rava.page.content()
        self.soup = BeautifulSoup(self.rendered_html, "html.parser")

        return self.rendered_html

    # --------------------------------------------------
    async def fetch_cash_flow_table(self) -> List[RavaBondCashFlow]:
        # Process HTML with BeautifulSoup
        table = await asyncio.to_thread(self.soup.select_one, "#scroll-flujo table")

        # Extract rows
        data = []
        rows = await asyncio.to_thread(table.find_all, "tr")
        rows = rows[1:]  # Skip header row
        for row in rows:
            cols = [td.text.strip() for td in row.find_all("td")]
            data.append(
                RavaBondCashFlow(
                    symbol=self.extract_sibling_text("Símbolo"),
                    date=parse_date(cols[0]),
                    interest=to_float(cols[1], 0),
                    amortization=to_float(cols[2], 0),
                    coupon=to_float(cols[3], 0),
                )
            )

        return data

    # --------------------------------------------------
    async def scrape_bond_data(self) -> RavaBondProfile:
        """Extract bond data from the rendered HTML"""
        # Extraer valores de forma asincrónica
        tir = await asyncio.to_thread(
            self.extract_text, "p:-soup-contains('Tasa interna de retorno (TIR)') span"
        )
        dm = await asyncio.to_thread(
            self.extract_text, "p:-soup-contains('Duration modificada (DM)') span"
        )

        bond_data = {
            "symbol": await asyncio.to_thread(self.extract_sibling_text, "Símbolo"),
            "denomination": await asyncio.to_thread(
                self.extract_sibling_text, "Denominación"
            ),
            "issuer": await asyncio.to_thread(self.extract_sibling_text, "Emisor"),
            "law": await asyncio.to_thread(self.extract_sibling_text, "Ley"),
            "currency": await asyncio.to_thread(
                self.extract_sibling_text, "Moneda de emisión"
            ),
            "issue_date": parse_date(
                await asyncio.to_thread(self.extract_sibling_text, "Fecha de Emisión"),
                "%d/%m/%Y",
            ),
            "maturity_date": parse_date(
                await asyncio.to_thread(self.extract_sibling_text, "Fecha Vencimiento"),
                "%d/%m/%Y",
            ),
            "nominal_amount": to_float(
                await asyncio.to_thread(
                    self.extract_sibling_text, "Monto nominal vigente"
                )
            ),
            "residual_amount": to_float(
                await asyncio.to_thread(self.extract_sibling_text, "Monto residual")
            ),
            "interest_description": await asyncio.to_thread(
                self.extract_sibling_text, "Interés"
            ),
            "amortization_description": await asyncio.to_thread(
                self.extract_sibling_text, "Forma de amortización"
            ),
            "minimum_denomination": to_float(
                await asyncio.to_thread(
                    self.extract_sibling_text, "Denominación mínima"
                )
            ),
            "tir": to_float(tir.replace("%", "")),
            "dm": to_float(dm),
        }

        return RavaBondProfile(**bond_data)


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()
    symbol = args.symbol

    async with async_playwright() as p:
        url = f"https://www.rava.com/perfil/{symbol}"
        rava = await connect_rava(playwright=p, headless=False, url=url)
        try:
            rava_bond_info = ScrapRavaBondInfo(rava=rava)
            await rava_bond_info.get_rendered_html()
            # # Guardar el HTML renderizado en un archivo para inspeccionarlo
            # with open("html_renderizado.html", "w", encoding="utf-8") as f:
            #     f.write(rava_bond_profile.rendered_html)

            # print(
            #     "✅ HTML renderizado guardado en 'html_renderizado.html'. Ábrelo en el navegador para inspeccionarlo."
            # )
            bond_data = await rava_bond_info.scrape_bond_data()
            print(bond_data)
            bonds = await rava_bond_info.fetch_cash_flow_table()
            for bond in bonds[:5]:  # Show only the first 5 bonds
                print(bond)
        except Exception as e:
            print(f"❌ Error: {e}")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.rava.handleres.scrap_bond_info
    # poetry run python -m src.rava.handleres.scrap_bond_info
