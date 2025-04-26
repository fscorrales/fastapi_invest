__all__ = ["format_instruments"]

from typing import List, Union

from ..schemas import SettlementTerm


# --------------------------------------------------
def format_instruments(
    symbols: Union[List[str], str],
    settlement_terms: Union[List[SettlementTerm], SettlementTerm] = ["CI", "24hs"],
) -> List[str]:
    """Get formatted instruments from symbols"""
    if not isinstance(symbols, list):
        # Si symbols es un único símbolo, lo convertimos en una lista
        symbols = [symbols]
    if not isinstance(settlement_terms, list):
        # Si settlement_terms es un único SettlementTerm, lo convertimos en una lista
        settlement_terms = [settlement_terms]
    formatted_instruments = [
        f"MERV - XMEV - {symbol} - {settlement_term}"
        for symbol in symbols
        for settlement_term in settlement_terms
    ]
    return formatted_instruments
