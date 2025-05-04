# src/strategies/services/strategy_manager.py


class StrategyManager:
    def __init__(self):
        self.strategies = {}

    def register(self, name: str, strategy):
        self.strategies[name] = strategy

    def stop_strategy(self, name: str):
        if name in self.strategies:
            self.strategies[name].stop()
            del self.strategies[name]

    def is_running(self, name: str):
        return name in self.strategies


strategy_manager = StrategyManager()
