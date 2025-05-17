__all__ = ["BaseWebsocket"]

from abc import ABC, abstractmethod

import pandas as pd


# --------------------------------------------------
class BaseWebsocket(ABC):
    # --------------------------------------------------
    def __init__(self):
        self.market_data_df = pd.DataFrame()

    # --------------------------------------------------
    @abstractmethod
    async def connect(self):
        pass

    # --------------------------------------------------
    def get_dataframe(self):
        return self.market_data_df.copy()
