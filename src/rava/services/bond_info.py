from typing import Annotated, List

from fastapi import Depends
from playwright.async_api import async_playwright

from ...config import logger

# from ...config import COLLECTIONS, db, logger
from ..handleres import ScrapRavaBondInfo
from ..schemas import RavaBondCashFlow, RavaBondProfile


class BondInfoService:
    def __init__(self) -> None:
        # assert (collection_name := "siif_rf602") in COLLECTIONS
        # self.collection = db[collection_name]
        self.bond_info = ScrapRavaBondInfo()

    async def get_bond_profile(
        self, symbol: str = "AL30", headless: bool = False
    ) -> RavaBondProfile:
        async with async_playwright() as p:
            try:
                await self.bond_info.connect(playwright=p, headless=headless)
                await self.bond_info.get_rendered_html(symbol=symbol)
                return await self.bond_info.scrape_bond_data()
            except Exception as e:
                logger.error(f"❌ Error: {e}")

    async def get_bond_cash_flow(
        self, symbol: str = "AL30", headless: bool = False
    ) -> List[RavaBondCashFlow]:
        async with async_playwright() as p:
            try:
                await self.bond_info.connect(playwright=p, headless=headless)
                await self.bond_info.get_rendered_html(symbol=symbol)
                return await self.bond_info.fetch_cash_flow_table()
            except Exception as e:
                logger.error(f"❌ Error: {e}")


BondInfoServiceDependency = Annotated[BondInfoService, Depends()]
