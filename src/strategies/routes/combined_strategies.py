# src/stretegies/routes/combined_strategies.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...primary.schemas import (
    PrimaryCredentials,
)
from ...primary.services import (
    WSMarketDataServiceDependency,
    prepare_primary_credentials,
)

from ..services import (
    strategy_manager,
    TimeArbitrageService,
    OptionCoberedCallService,
    TIME_ARBITRAGE_NAME,
    OPTION_COBERED_CALL_NAME,
)

STRATEGY_NAME = "combined_strategies"

combined_strategies_router = APIRouter(
    prefix="/" + STRATEGY_NAME, tags=["Strategies - Combined Strategies"]
)


@combined_strategies_router.post("/start_all")
async def start_all(
    auth: OptionalAuthorizationDependency,
    service: WSMarketDataServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    days: int = 1,
):

    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    strategy = TimeArbitrageService(market_data_service=service, days=days)
    strategy_manager.register(TIME_ARBITRAGE_NAME, strategy)
    strategy = OptionCoberedCallService(market_data_service=service, days=days)
    strategy_manager.register(OPTION_COBERED_CALL_NAME, strategy)

    await strategy_manager.start_all(credentials)
    return {"status": "Todas las estrategias iniciadas"}

@combined_strategies_router.post("/stop_all")
async def stop_all():
    strategy_manager.stop_all()
    return {"status": "Todas las estrategias detenidas"}

@combined_strategies_router.get("/status")
def list_running():
    return {"running": strategy_manager.list_active()}
