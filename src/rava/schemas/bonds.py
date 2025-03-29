__all__ = ["RavaBond", "RavaBondProfile", "RavaBondCashFlow"]

from datetime import date, time
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


class RavaBondProfile(BaseModel):
    # Profile details
    symbol: str
    denomination: str
    issuer: str
    law: str
    currency: str
    issue_date: Optional[date] = None
    maturity_date: Optional[date] = None
    nominal_amount: Optional[float] = None
    residual_amount: Optional[float] = None
    interest_description: str
    amortization_description: str
    minimum_denomination: Optional[float] = None
    tir: Optional[float] = None
    dm: Optional[float] = None


class RavaBondCashFlow(BaseModel):
    symbol: str
    date: date
    interest: float
    amortization: float
    coupon: float
