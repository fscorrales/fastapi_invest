#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 27-mar-2025
Purpose: Scrapt Bonds from RAVA
"""

__all__ = ["scrapt_bonds", "get_rendered_html"]

import argparse
import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Scrapt Bonds from RAVA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
async def get_rendered_html(url: str = None):
    if url is None:
        url = "https://www.rava.com/cotizaciones/bonos"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )  # Change to False if you want to see the browser
        page = await browser.new_page()
        await page.goto(url)

        # Wait for the bonds table to appear (adjust selector if necessary)
        await page.wait_for_selector("table")

        # Get the rendered HTML
        rendered_html = await page.content()
        await browser.close()

        return rendered_html


# --------------------------------------------------
def scrapt_bonds(html):
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

        bond = {
            "symbol": symbol,
            "link": href,
            "close": cells[1].text.strip(),
            "var_day": cells[2].text.strip(),
            "var_month": cells[3].text.strip(),
            "var_year": cells[4].text.strip(),
            "previous_close": cells[5].text.strip(),
            "open": cells[6].text.strip(),
            "low": cells[7].text.strip(),
            "high": cells[8].text.strip(),
            "time": cells[9].text.strip(),
            "nominal_volume": cells[10].text.strip(),
            "effective_volume": cells[11].text.strip(),
        }
        bonds.append(bond)

    return bonds


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    html = await get_rendered_html()
    bonds = scrapt_bonds(html)

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

    # python -m src.rava.handleres.extract_bonds

    # ╔════════════════════════════════════════════════════════════╗
    # ║ WARNING: Playwright browsers not found.                    ║
    # ║ Looks like Playwright was just installed or updated.       ║
    # ║ Please run the following command to download new browsers: ║
    # ║                                                            ║
    # ║     playwright install                                     ║
    # ║                                                            ║
    # ║ <3 Playwright Team
