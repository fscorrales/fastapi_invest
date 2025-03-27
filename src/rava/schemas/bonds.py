__all__ = ["RavaBond"]

from datetime import time
from typing import Optional

from pydantic import BaseModel, NonNegativeFloat


class RavaBond(BaseModel):
    """Schema for bonds scraped from RAVA"""

    symbol: str
    link: str
    close: Optional[NonNegativeFloat] = None
    var_day: Optional[float] = None
    var_month: Optional[float] = None
    var_year: Optional[float] = None
    previous_close: Optional[NonNegativeFloat] = None
    open: Optional[NonNegativeFloat] = None
    low: Optional[NonNegativeFloat] = None
    high: Optional[NonNegativeFloat] = None
    time: time
    nominal_volume: Optional[NonNegativeFloat] = None
    effective_volume: Optional[NonNegativeFloat] = None
