__all__ = [
    "to_float",
    "parse_date",
    "convert_str_column_to_datetime_safe",
    "convert_str_to_date_only_safe",
]

from datetime import date, datetime
from typing import Optional

import pandas as pd


# --------------------------------------------------
def to_float(value: str, default: Optional[float] = None) -> Optional[float]:
    """Convert a string to float, or return default if conversion fails."""
    try:
        value = value.replace(".", "")
        value = value.replace(",", ".")
        return float(value.strip())  # Remove commas if present
    except (ValueError, AttributeError):
        return default


# --------------------------------------------------
def parse_date(date_str: str, fmt: str = "%d/%m/%Y") -> date:
    return datetime.strptime(date_str, fmt).date()


# --------------------------------------------------
def convert_str_column_to_datetime_safe(col: pd.Series, fmt: str = None) -> pd.Series:
    return pd.to_datetime(col, errors="coerce", format=fmt).apply(
        lambda x: x.to_pydatetime() if pd.notnull(x) else None
    )


# --------------------------------------------------
def convert_str_to_date_only_safe(col: pd.Series, fmt: str = None) -> pd.Series:
    return pd.to_datetime(col, errors="coerce", format=fmt).apply(
        lambda x: x.date() if pd.notnull(x) else None
    )
