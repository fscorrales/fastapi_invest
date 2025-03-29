#!/usr/bin/env python3
"""
Author : Fernando Corrales <fscpython@gamail.com>
Date   : 29-mar-2025
Purpose: Go to RAVA´s page (homepage by default)
"""

__all__ = ["RavaConnection", "connect_rava", "RavaManager"]

import argparse
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

from bs4 import BeautifulSoup
from playwright._impl._browser import Browser, BrowserContext, Page
from playwright.async_api import Playwright, async_playwright

from ...utils import extract_sibling_text, extract_text


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
    url: str = None,
) -> RavaConnection:
    if playwright is None:
        playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=headless  # args=["--start-maximized"]
    )
    context = await browser.new_context(no_viewport=True)
    page = await context.new_page()

    if url is not None:
        try:
            "Open Rava's page (homepage by default)"
            # url = "https://rava.com/"
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Ocurrio un error: {e}")

    return RavaConnection(browser=browser, context=context, page=page, url=url)


# --------------------------------------------------
@dataclass
class RavaManager(ABC):
    rava: RavaConnection = None
    rendered_html: str = None
    soup: BeautifulSoup = None

    # --------------------------------------------------
    async def connect(
        self,
        playwright: Playwright,
        headless: bool = False,
        url: str = None,
    ) -> RavaConnection:
        self.rava = await connect_rava(
            playwright=playwright, headless=headless, url=url
        )
        return self.rava

    # --------------------------------------------------
    @abstractmethod
    async def get_rendered_html(self) -> None:
        """Go to specific report"""
        pass

    # --------------------------------------------------
    def extract_text(self, selector: str) -> str:
        """Extract text from the HTML using a CSS selector."""
        if self.rendered_html is None:
            raise ValueError("Rendered HTML is not available.")

        return extract_text(selector, soup=self.soup)

    # --------------------------------------------------
    def extract_sibling_text(self, label: str, tag_name: str = "b") -> str:
        """Extract text from the HTML using a CSS selector."""
        if self.rendered_html is None:
            raise ValueError("Rendered HTML is not available.")

        return extract_sibling_text(label, soup=self.soup, tag_name=tag_name)


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
