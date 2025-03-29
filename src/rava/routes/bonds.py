from typing import List

from fastapi import APIRouter

from ..schemas import RavaBondCashFlow, RavaBondProfile
from ..services import BondInfoServiceDependency

bonds_router = APIRouter(prefix="/bonds", tags=["Rava - Bonds"])


@bonds_router.get("/profile", response_model=RavaBondProfile)
async def rava_bond_profile(
    service: BondInfoServiceDependency, symbol: str = "AL30", hide_browser: bool = True
):
    return await service.get_bond_profile(symbol=symbol, headless=hide_browser)


@bonds_router.get("/cash_flow", response_model=List[RavaBondCashFlow])
async def rava_bond_cash_flow(
    service: BondInfoServiceDependency, symbol: str = "AL30", hide_browser: bool = True
):
    return await service.get_bond_cash_flow(symbol=symbol, headless=hide_browser)
