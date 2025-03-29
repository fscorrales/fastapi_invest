#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 27-mar-2025
Purpose: Scrap Bonds from RAVA
"""

__all__ = ["fetch_cash_flow_table", "get_bond_info_rendered_html", "scrape_bond_data"]

import argparse
import asyncio
from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from ...utils import extract_sibling_text, extract_text, parse_date, to_float
from ..schemas import RavaBondCashFlow, RavaBondProfile


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Scrap Bonds from RAVA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "symbol", metavar="str", help="Bond symbol", type=str, default="AL30"
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
async def get_bond_info_rendered_html(symbol: str = None, url: str = None) -> str:
    """Get the rendered HTML of the RAVA bonds page using Playwright"""
    if symbol is not None:
        url = f"https://www.rava.com/perfil/{symbol}"
    elif url is None:
        url = "https://www.rava.com/perfil/AL30"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False
        )  # Change to False if you want to see the browser
        page = await browser.new_page()
        await page.goto(url, timeout=30000)

        # Wait for the bonds table to appear (adjust selector if necessary)
        await page.wait_for_selector("table", timeout=15000)  # Wait 15 seconds

        # Get the rendered HTML
        rendered_html = await page.content()
        await browser.close()

        return rendered_html


# --------------------------------------------------
def fetch_cash_flow_table(html: str) -> List[RavaBondCashFlow]:
    # Process HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#scroll-flujo table")

    # Extract rows
    data = []
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        cols = [td.text.strip() for td in row.find_all("td")]
        data.append(
            RavaBondCashFlow(
                symbol=extract_sibling_text("Símbolo", soup),
                date=parse_date(cols[0]),
                interest=to_float(cols[1], 0),
                amortization=to_float(cols[2], 0),
                coupon=to_float(cols[3], 0),
            )
        )

    return data


# --------------------------------------------------
def scrape_bond_data(html: str) -> RavaBondProfile:
    pass  # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    tir = extract_text("p:contains('Tasa interna de retorno (TIR)') span", soup)
    dm = extract_text("p:contains('Duration modificada (DM)') span", soup)

    bond_data = {
        "symbol": extract_sibling_text("Símbolo", soup),
        "denomination": extract_sibling_text("Denominación", soup),
        "issuer": extract_sibling_text("Emisor", soup),
        "law": extract_sibling_text("Ley", soup),
        "currency": extract_sibling_text("Moneda de emisión", soup),
        "issue_date": parse_date(
            extract_sibling_text("Fecha de Emisión", soup), "%d/%m/%Y"
        ),
        "maturity_date": parse_date(
            extract_sibling_text("Fecha Vencimiento", soup), "%d/%m/%Y"
        ),
        "nominal_amount": to_float(extract_sibling_text("Monto nominal vigente", soup)),
        "residual_amount": to_float(extract_sibling_text("Monto residual", soup)),
        "interest_description": extract_sibling_text("Interés", soup),
        "amortization_description": extract_sibling_text("Forma de amortización", soup),
        "minimum_denomination": to_float(
            extract_sibling_text("Denominación mínima", soup)
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

    html = await get_bond_info_rendered_html(symbol=symbol)

    bond_data = scrape_bond_data(html)
    print(bond_data)

    bonds = fetch_cash_flow_table(html)
    for bond in bonds[:5]:  # Show only the first 5 bonds
        print(bond)

    # html = await get_rendered_html(symbol=symbol)

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

    # python -m src.rava.handleres.scrap_bond_info AL30

    # ╔════════════════════════════════════════════════════════════╗
    # ║ WARNING: Playwright browsers not found.                    ║
    # ║ Looks like Playwright was just installed or updated.       ║
    # ║ Please run the following command to download new browsers: ║
    # ║                                                            ║
    # ║     playwright install                                     ║
    # ║                                                            ║
    # ║ <3 Playwright Team
