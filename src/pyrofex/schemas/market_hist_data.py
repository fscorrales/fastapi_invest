__all__ = ["ParamsMarketHistData", "MarketHistData"]

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import Enviroment, InstrumentID, MarketID


class ParamsMarketHistData(BaseModel):
    marketId: MarketID
    symbol: str
    # date: Optional[str] = Field(None, description="Date in format YYYY-MM-DD")
    dateFrom: Optional[str] = Field(None, description="Start date in format YYYY-MM-DD")
    dateTo: Optional[str] = Field(None, description="End date in format YYYY-MM-DD")
    external: bool = False
    environment: Enviroment = Enviroment.remarkets

    # @field_validator("date", "dateFrom", "dateTo")
    # def validate_date_format(cls, v, info):
    #     if v:
    #         try:
    #             datetime.strptime(v, "%Y-%m-%d")
    #         except ValueError:
    #             raise ValueError(
    #                 f"{info.field_name} must be a valid date in YYYY-MM-DD format"
    #             )
    #     return v

    # @model_validator(mode="after")
    # def check_date_combination(self):
    #     if not self.date and not (self.dateFrom and self.dateTo):
    #         raise ValueError(
    #             "You must provide either 'date' or both 'dateFrom' and 'dateTo'"
    #         )
    #     return self


# --------------------------------------------------
class MarketHistData(InstrumentID):
    enviroment: Enviroment
