__all__ = ["strategies_router"]

from fastapi import APIRouter

from .combined_strategies import combined_strategies_router
from .option_cobered_call import option_cobered_call_router
from .option_necklace import option_necklace_router
from .time_arbitrage import time_arbitrage_router

strategies_router = APIRouter(prefix="/strategies")

strategies_router.include_router(combined_strategies_router)
strategies_router.include_router(time_arbitrage_router)
strategies_router.include_router(option_cobered_call_router)
strategies_router.include_router(option_necklace_router)
