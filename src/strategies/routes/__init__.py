__all__ = ["strategies_router"]

from fastapi import APIRouter

from .time_arbitrage import time_arbitrage_router

strategies_router = APIRouter(prefix="/strategies")

strategies_router.include_router(time_arbitrage_router)
