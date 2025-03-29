#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 27-mar-2025
Purpose: Scrap Bonds from RAVA
"""

__all__ = ["RavaBonds"]

import argparse
import asyncio
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from ...utils import to_float
from ..schemas import RavaBond
from .connect import RavaConnection, connect_rava


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Scrap Bonds from RAVA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u",
        "--url",
        help="Rava's page URL",
        metavar="str",
        type=str,
        default="https://www.rava.com/cotizaciones/bonos",
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
@dataclass
class RavaBonds:
    rava: RavaConnection
    rendered_html: str = None

    # --------------------------------------------------
    async def get_rendered_html(self, url: str = None) -> str:
        """Get the rendered HTML of the RAVA bonds page using Playwright"""
        if url is None:
            url = "https://www.rava.com/cotizaciones/bonos"

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
        return self.rendered_html

    # --------------------------------------------------
    def scrap_bonds(self) -> List[RavaBond]:
        """Extract the bonds table from the rendered HTML"""
        soup = BeautifulSoup(self.rendered_html, "html.parser")
        table = soup.find("table")

        if not table:
            print("❌ Table not found.")
            return []

        bonds = []
        rows = table.find_all("tr")[1:]  # Skip the header row

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 11:  # Ensure there are enough columns
                continue

            # Extract bond symbol and link
            symbol_tag = cells[0].find("a")
            symbol = symbol_tag.text.strip() if symbol_tag else cells[0].text.strip()
            href = symbol_tag["href"] if symbol_tag else ""

            bond = RavaBond(
                symbol=symbol,
                link="https://www.rava.com" + href,
                close=to_float(cells[1].text),
                var_day=to_float(cells[2].text),
                var_month=to_float(cells[3].text),
                var_year=to_float(cells[4].text),
                previous_close=to_float(cells[5].text),
                open=to_float(cells[6].text),
                low=to_float(cells[7].text),
                high=to_float(cells[8].text),
                time=cells[9].text,
                nominal_volume=to_float(cells[10].text),
                effective_volume=to_float(cells[11].text),
            )
            bonds.append(bond)

        return bonds


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()
    url = args.url

    async with async_playwright() as p:
        rava = await connect_rava(playwright=p, headless=False, url=url)
        try:
            rava_bonds = RavaBonds(rava=rava)
            await rava_bonds.get_rendered_html()
            bonds = rava_bonds.scrap_bonds()
            for bond in bonds[:5]:  # Show only the first 5 bonds
                print(bond)
        except Exception as e:
            print(f"❌ Error: {e}")

    # html = await obtener_html_renderizado()

    # # Guardar el HTML renderizado en un archivo para inspeccionarlo
    # with open("html_renderizado.html", "w", encoding="utf-8") as f:
    #     f.write(html)

    # print(
    #     "✅ HTML renderizado guardado en 'html_renderizado.html'. Ábrelo en el navegador para inspeccionarlo."
    # )


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.rava.handleres.scrap_bonds
    # poetry run python -m src.rava.handleres.scrap_bonds

    # ╔════════════════════════════════════════════════════════════╗
    # ║ WARNING: Playwright browsers not found.                    ║
    # ║ Looks like Playwright was just installed or updated.       ║
    # ║ Please run the following command to download new browsers: ║
    # ║                                                            ║
    # ║     playwright install                                     ║
    # ║                                                            ║
    # ║ <3 Playwright Team
