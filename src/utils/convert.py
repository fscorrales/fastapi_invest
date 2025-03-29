__all__ = ["to_float", "parse_date"]

from datetime import date, datetime
from typing import Optional


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
