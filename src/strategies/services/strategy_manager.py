# src/strategies/services/strategy_manager.py

__all__ = ["strategy_manager"]

from typing import Dict

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

    # -------------------------------------------------
    def stop_strategy(self, name: str):
        if name in self.strategies:
            self.strategies[name].stop()
            del self.strategies[name]

    # -------------------------------------------------
    async def start_all(self):
        for strategy in self.strategies.values():
            await strategy.start()
            
    # -------------------------------------------------
    def stop_all(self):
        for strategy in self.strategies.values():
            strategy.stop()

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
