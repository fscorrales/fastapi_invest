# src/stretegies/routes/strategies.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...primary.schemas import (
    PrimaryCredentials,
    WSMarketDataParams,
)
from ...primary.services import (
    WSMarketDataServiceDependency,
    prepare_primary_credentials,
)
from ..services import TimeArbitrageStrategy, strategy_manager

strategies_router = APIRouter(prefix="/strategies", tags=["Strategies"])


@strategies_router.post("/time_arbitrage", response_model=dict)
async def time_arbitrage(
    auth: OptionalAuthorizationDependency,
    service: WSMarketDataServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
):
    if service.task and not service.task.done():
        raise HTTPException(status_code=400, detail="WebSocket stream already running.")

    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    strategy_name = "time_arbitrage_GGAL"

    if strategy_name in strategy_manager.list_active():
        raise HTTPException(status_code=400, detail="La estrategia ya está corriendo")

    strategy = TimeArbitrageStrategy(market_data_service=service)
    strategy_manager.register(strategy_name, strategy)
    strategy_manager.start(strategy_name, credentials)  # AQUI EL ERROR

    return {"message": f"Estrategia '{strategy_name}' iniciada"}

    # return await service.stream_market_data(
    #     credentials=credentials,
    #     params=params,
    # )


# class StartRequest(BaseModel):
#     symbol: str


# @router.post("/start")
# async def start_time_arbitrage(
#     request: StartRequest,
#     service: WSMarketDataServiceDependency,
# ):
#     strategy_name = "time_arbitrage"
#     if strategy_manager.is_running(strategy_name):
#         raise HTTPException(status_code=400, detail="Strategy already running.")

#     strategy = TimeArbitrageStrategy(service=service, symbol=request.symbol)
#     strategy_manager.register(strategy_name, strategy)
#     strategy.start()

#     return {"status": "started", "strategy": strategy_name}


# @router.post("/stop")
# async def stop_time_arbitrage():
#     strategy_name = "time_arbitrage"
#     strategy_manager.stop_strategy(strategy_name)
#     return {"status": "stopped", "strategy": strategy_name}
