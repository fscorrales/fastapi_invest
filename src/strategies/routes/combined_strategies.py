# src/stretegies/routes/combined_strategies.py

from typing import Annotated

from fastapi import APIRouter, Depends, Query

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
    OPTION_COBERED_CALL_NAME,
    TIME_ARBITRAGE_NAME,
    OptionCoberedCallService,
    TimeArbitrageService,
    strategy_manager,
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
    upload_to_google_sheets: bool = Query(False, alias="uploadToGoogleSheets"),
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    strategy = TimeArbitrageService(
        market_data_service=service,
        days=days,
        upload_to_google_sheets=upload_to_google_sheets,
    )
    if TIME_ARBITRAGE_NAME in strategy_manager.list_active():
        logger.warning("La estrategia de arbitraje de tiempo ya está corriendo")
    else:
        logger.info("Registrando la estrategia de arbitraje de tiempo")
    strategy_manager.register(TIME_ARBITRAGE_NAME, strategy)
    strategy = OptionCoberedCallService(
        market_data_service=service,
        days=days,
        upload_to_google_sheets=upload_to_google_sheets,
    )
    if OPTION_COBERED_CALL_NAME in strategy_manager.list_active():
        logger.warning("La estrategia de opción cubierta ya está corriendo")
    else:
        logger.info("Registrando la estrategia de opción cubierta")
    strategy_manager.register(OPTION_COBERED_CALL_NAME, strategy)

    await strategy_manager.start_all(credentials)
    return {"status": "Todas las estrategias iniciadas"}


@combined_strategies_router.post("/stop_all")
async def stop_all():
    await strategy_manager.stop_all()
    return {"status": "Todas las estrategias detenidas"}


@combined_strategies_router.get("/status")
def list_running():
    return {"running": strategy_manager.list_active()}
