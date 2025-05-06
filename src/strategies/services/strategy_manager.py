# src/strategies/services/strategy_manager.py

__all__ = ["strategy_manager"]


class StrategyManager:
    def __init__(self):
        self.strategies = {}

    def register(self, name: str, strategy):
        self.strategies[name] = strategy

    def start_strategy(self, name: str, *args, **kwargs):
        if name not in self.strategies:
            raise ValueError(f"Estrategia '{name}' no existe")
        self.strategies[name].start(*args, **kwargs)

    def stop_strategy(self, name: str):
        if name in self.strategies:
            self.strategies[name].stop()
            del self.strategies[name]

    def is_running(self, name: str):
        return name in self.strategies

    def list_active(self):
        return [name for name, strat in self.strategies.items() if strat.is_running()]


strategy_manager = StrategyManager()
