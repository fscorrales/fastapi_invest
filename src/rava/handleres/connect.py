#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 29-mar-2025
Purpose: Go to RAVA´s page (homepage by default)
"""

__all__ = ["RavaConnection", "connect_rava"]

import argparse
import asyncio
from dataclasses import dataclass

from playwright._impl._browser import Browser, BrowserContext, Page
from playwright.async_api import Playwright, async_playwright


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Go to RAVA´s page (homepage by default)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-u",
        "--url",
        help="Rava's page URL",
        metavar="str",
        type=str,
        default="https://rava.com/",
    )

    args = parser.parse_args()

    return args


# --------------------------------------------------
@dataclass
class RavaConnection:
    browser: Browser = None
    context: BrowserContext = None
    page: Page = None
    url: str = None


# --------------------------------------------------
async def connect_rava(
    playwright: Playwright = None,
    headless: bool = False,
    url: str = "https://rava.com/",
) -> RavaConnection:
    if playwright is None:
        playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=headless  # args=["--start-maximized"]
    )
    context = await browser.new_context(no_viewport=True)
    page = await context.new_page()

    try:
        "Open Rava's page (homepage by default)"
        # url = "https://rava.com/"
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
    except Exception as e:
        print(f"Ocurrio un error: {e}")

    return RavaConnection(browser=browser, context=context, page=page, url=url)


# --------------------------------------------------
async def main():
    """Make a jazz noise here"""

    args = get_args()
    url = args.url

    async with async_playwright() as playwright:
        rava = await connect_rava(playwright=playwright, headless=False, url=url)
        # rava = await connect(playwright=playwright, headless=True)

        # Do something with the connection
        # Example: await rava.page.screenshot(path="screenshot.png")


# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
    # From /fastapi_invest

    # python -m src.rava.handleres.connect
    # poetry run python -m src.rava.handleres.connect

    # ╔════════════════════════════════════════════════════════════╗
    # ║ WARNING: Playwright browsers not found.                    ║
    # ║ Looks like Playwright was just installed or updated.       ║
    # ║ Please run the following command to download new browsers: ║
    # ║                                                            ║
    # ║     playwright install                                     ║
    # ║                                                            ║
    # ║ <3 Playwright Team
