# src/stretegies/routes/option_cobered_call.py

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
)

STRATEGY_NAME = "combined_strategies"

combined_strategies_router = APIRouter(
    prefix="/" + STRATEGY_NAME, tags=["Strategies - Combined Strategies"]
)


@combined_strategies_router.post("/start_all")
async def start_all():
    await strategy_manager.start_all()
    return {"status": "Todas las estrategias iniciadas"}

@combined_strategies_router.post("/stop_all")
async def stop_all():
    await strategy_manager.stop_all()
    return {"status": "Todas las estrategias detenidas"}

@combined_strategies_router.get("/status")
def list_running():
    return {"running": strategy_manager.list_active()}
