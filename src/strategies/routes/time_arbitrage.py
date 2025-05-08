# src/stretegies/routes/strategies.py

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
from ..schemas import TimeArbitrageSummary
from ..services import (
    TimeArbitrageStrategyDependency,
    TimeArbitrageStrategyService,
    strategy_manager,
)

time_arbitrage_router = APIRouter(
    prefix="/time_arbitrage", tags=["Strategies - Time Arbitrage"]
)


@time_arbitrage_router.post("/start", response_model=dict)
async def start_time_arbitrage(
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

    strategy_name = "time_arbitrage"

    if strategy_name in strategy_manager.list_active():
        raise HTTPException(status_code=400, detail="La estrategia ya está corriendo")

    strategy = TimeArbitrageStrategyService(market_data_service=service)
    strategy_manager.register(strategy_name, strategy)
    await strategy_manager.start_strategy(strategy_name, credentials)

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


@time_arbitrage_router.post("/stop")
async def stop_time_arbitrage():
    strategy_name = "time_arbitrage"
    strategy_manager.stop_strategy(strategy_name)
    return {"status": "stopped", "strategy": strategy_name}


@time_arbitrage_router.post("/reset", response_model=dict)
async def reset_strategy_data(
    service: TimeArbitrageStrategyDependency,
):
    service.reset_dataframe()
    return {"message": "DataFrame reseteado correctamente."}


@time_arbitrage_router.get("/dataframe", response_model=list[TimeArbitrageSummary])
async def get_strategy_data(
    service: TimeArbitrageStrategyDependency,
):
    df = service.get_dataframe()
    if df.empty:
        raise HTTPException(status_code=404, detail="No hay datos disponibles")
    return [TimeArbitrageSummary(**row.to_dict()) for _, row in df.iterrows()]
