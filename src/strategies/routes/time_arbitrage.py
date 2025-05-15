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
from ...utils import apply_auto_filter
from ..schemas import TimeArbitrageFilter, TimeArbitrageSummary
from ..services import (
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


@time_arbitrage_router.get("/status", response_model=dict)
async def get_strategy_status():
    is_running = "time_arbitrage" in strategy_manager.list_active()
    return {
        "strategy": "time_arbitrage",
        "status": "running" if is_running else "stopped",
    }


@time_arbitrage_router.post("/stop")
async def stop_time_arbitrage():
    strategy_name = "time_arbitrage"
    strategy_manager.stop_strategy(strategy_name)
    return {"status": "stopped", "strategy": strategy_name}


@time_arbitrage_router.post("/reset", response_model=dict)
async def reset_strategy_data():
    strategy = strategy_manager.get("time_arbitrage")
    if not strategy:
        raise HTTPException(status_code=404, detail="La estrategia no está activa")

    strategy.reset_dataframe()
    return {"message": "DataFrame reseteado correctamente."}


@time_arbitrage_router.get("/dataframe", response_model=list[TimeArbitrageSummary])
async def get_strategy_data(
    params: Annotated[TimeArbitrageFilter, Depends()],
):
    strategy = strategy_manager.get("time_arbitrage")
    if not strategy:
        raise HTTPException(status_code=404, detail="La estrategia no está activa")

    df = strategy.get_dataframe()
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No hay datos disponibles")

    # Aplicar filtros
    apply_auto_filter(params)
    query = params.get_full_filter()

    # --- Aplicamos el filtro al DataFrame ---
    if query:
        for key, condition in query.items():
            if "$eq" in condition:
                df = df[df[key] == condition["$eq"]]

    # Ordenamiento
    if params.sort_by in df.columns:
        ascending = params.sort_dir == "asc"
        df = df.sort_values(by=params.sort_by, ascending=ascending)

    # Paginación
    df = df.iloc[params.offset : params.offset + params.limit]

    return [TimeArbitrageSummary(**row.to_dict()) for _, row in df.iterrows()]
