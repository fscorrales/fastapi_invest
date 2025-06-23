# src/stretegies/routes/combined_strategies.py

from typing import Annotated, List, Tuple, Type

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
    OPTION_BEAR_SPREAD_NAME,
    OPTION_BULL_SPREAD_NAME,
    OPTION_CALL_RATIO_BACKSPREAD_NAME,
    OPTION_COBERED_CALL_NAME,
    OPTION_LONG_WINGS_NAME,
    OPTION_MARKET_DATA_NAME,
    OPTION_NECKLACE_NAME,
    OPTION_PUT_RATIO_BACKSPREAD_NAME,
    TIME_ARBITRAGE_NAME,
    BaseStrategy,
    OptionBearSpreadService,
    OptionBullSpreadService,
    OptionCallRatioBackspreadService,
    OptionCoberedCallService,
    OptionLongWingsService,
    OptionMarketDataService,
    OptionNecklaceService,
    OptionPutRatioBackspreadService,
    TimeArbitrageService,
    strategies_manager,
)

STRATEGY_NAME = "combined_strategies"

combined_strategies_router = APIRouter(
    prefix="/" + STRATEGY_NAME, tags=["Strategies - Combined Strategies"]
)

# Lista de estrategias con su nombre y clase
STRATEGIES: List[Tuple[str, Type[BaseStrategy]]] = [
    (TIME_ARBITRAGE_NAME, TimeArbitrageService),
    (OPTION_MARKET_DATA_NAME, OptionMarketDataService),
    (OPTION_COBERED_CALL_NAME, OptionCoberedCallService),
    (OPTION_NECKLACE_NAME, OptionNecklaceService),
    (OPTION_BULL_SPREAD_NAME, OptionBullSpreadService),
    (OPTION_BEAR_SPREAD_NAME, OptionBearSpreadService),
    (OPTION_CALL_RATIO_BACKSPREAD_NAME, OptionCallRatioBackspreadService),
    (OPTION_PUT_RATIO_BACKSPREAD_NAME, OptionPutRatioBackspreadService),
    (OPTION_LONG_WINGS_NAME, OptionLongWingsService),
]


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

    for name, StrategyClass in STRATEGIES:
        if name in strategies_manager.list_active():
            logger.warning(f"La estrategia '{name}' ya está corriendo")
            continue

        logger.info(f"Registrando la estrategia '{name}'")
        strategy = StrategyClass(
            market_data_service=service,
            days=days,
            upload_to_google_sheets=upload_to_google_sheets,
            upload_interval=30,
        )
        strategies_manager.register(name, strategy)

    await strategies_manager.start_all(credentials)
    return {"status": "Todas las estrategias iniciadas"}


@combined_strategies_router.post("/stop_all")
async def stop_all():
    await strategies_manager.stop_all()
    return {"status": "Todas las estrategias detenidas"}


@combined_strategies_router.get("/status")
def list_running():
    return {"running": strategies_manager.list_active()}
