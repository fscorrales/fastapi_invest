# src/strategies/services/strategy_manager.py

__all__ = ["strategy_manager"]

from typing import Dict

from ...config import logger
from .base_strategy import BaseStrategy


# -------------------------------------------------
class StrategyManager:
    # -------------------------------------------------
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}

    # -------------------------------------------------
    def register(self, name: str, strategy: BaseStrategy):
        self.strategies[name] = strategy

    # -------------------------------------------------
    async def start_strategy(self, name: str, *args, **kwargs):
        if name not in self.strategies:
            raise ValueError(f"Estrategia '{name}' no existe")
        await self.strategies[name].start(*args, **kwargs)
        self.is_running

    # -------------------------------------------------
    async def stop_strategy(self, name: str):
        if name in self.strategies:
            await self.strategies[name].stop()
            if len(self.list_active()) == 0:
                logger.info(f"Desconectando WebSocket desde la estrategia '{name}'")
                await self.strategies[name].market_data_service.disconnect()
            del self.strategies[name]

    # -------------------------------------------------
    async def start_all(self, *args, **kwargs):
        for strategy in self.strategies.values():
            await strategy.start(*args, **kwargs)

    # -------------------------------------------------
    async def stop_all(self):
        # Detenemos todas las estrategias
        for strategy in self.strategies.values():
            await strategy.stop()

        # Desconectamos el WebSocket (compartido por todas)
        if self.strategies:
            first_strategy = next(iter(self.strategies.values()))
            if hasattr(first_strategy, "market_data_service"):
                await first_strategy.market_data_service.disconnect()

        # Limpiamos el registro
        self.strategies.clear()

    # -------------------------------------------------
    def get(self, name):
        return self.strategies.get(name)

    # -------------------------------------------------
    def is_running(self, name: str):
        return name in self.strategies

    # -------------------------------------------------
    def list_active(self):
        return [name for name, strat in self.strategies.items() if strat.is_running]

    # -------------------------------------------------
    @property
    def summary(self):
        return self.summary_strategy_df.copy()


strategy_manager = StrategyManager()
