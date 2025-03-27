#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 27-mar-2025
Purpose: Scrap Bonds from RAVA
"""

__all__ = ["scrap_bonds", "get_rendered_html"]

import argparse
import asyncio
from typing import List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from ..schemas import RavaBond


# --------------------------------------------------
def safe_float(value: str) -> Optional[float]:
    """Convert a string to float, or return None if conversion fails."""
    try:
        return float(value.replace(",", "").strip())  # Remove commas if present
    except (ValueError, AttributeError):
        return None


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Scrap Bonds from RAVA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
async def get_rendered_html(url: str = None) -> str:
    """Get the rendered HTML of the RAVA bonds page using Playwright"""
    if url is None:
        url = "https://www.rava.com/cotizaciones/bonos"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )  # Change to False if you want to see the browser
        page = await browser.new_page()
        await page.goto(url)

        # Wait for the bonds table to appear (adjust selector if necessary)
        await page.wait_for_selector("table", timeout=10000)  # Wait 10 seconds

        # Get the rendered HTML
        rendered_html = await page.content()
        await browser.close()

        return rendered_html


# --------------------------------------------------
def scrap_bonds(html) -> List[RavaBond]:
    """Extract the bonds table from the rendered HTML"""
    soup = BeautifulSoup(html, "html.parser")
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
            close=safe_float(cells[1].text),
            var_day=safe_float(cells[2].text),
            var_month=safe_float(cells[3].text),
            var_year=safe_float(cells[4].text),
            previous_close=safe_float(cells[5].text),
            open=safe_float(cells[6].text),
            low=safe_float(cells[7].text),
            high=safe_float(cells[8].text),
            time=cells[9].text,
            nominal_volume=safe_float(cells[10].text),
            effective_volume=safe_float(cells[11].text),
        )
        bonds.append(bond)

    return bonds


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    html = await get_rendered_html()
    bonds = scrap_bonds(html)

    for bond in bonds[:5]:  # Show only the first 5 bonds
        print(bond)

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

    # ╔════════════════════════════════════════════════════════════╗
    # ║ WARNING: Playwright browsers not found.                    ║
    # ║ Looks like Playwright was just installed or updated.       ║
    # ║ Please run the following command to download new browsers: ║
    # ║                                                            ║
    # ║     playwright install                                     ║
    # ║                                                            ║
    # ║ <3 Playwright Team
