__all__ = [
    "PrimaryCredentials",
    "Enviroment",
    "CFICode",
    "MarketSegmentID",
    "InstrumentID",
    "MarketID",
    "Entry",
    "Depth",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "OrderTimeInForce",
    "SettlementTerm",
    "SyncResult",
    "PriceWithSize",
    "PriceWithSizeAndDate",
    "MarketData",
]

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


# -------------------------------------------------
class Enviroment(str, Enum):
    """Ambiente de conexión."""

    live = "LIVE"
    remarkets = "REMARKETS"  # Ambiente de pruebas de Primary


# -------------------------------------------------
class PrimaryCredentials(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    enviroment: Enviroment


# -------------------------------------------------
class CFICode(str, Enum):
    """Código que identifica el tipo de instrumento."""

    accion = "ESXXXX"
    bono = "DBXXXX"
    call_accion = "OCASPS"
    put_accion = "OPASPS"
    futuro = "FXXXSX"
    put_futuro = "OPAFXS"
    call_futuro = "OCAFXS"
    cedear = "EMXXXX"
    on = "DBXXFR"
    indice = "MRIXXX"
    futuro_otro = "FXXXXX"
    letra = "DYXTXR"
    caucion = "RPXXXX"
    test_1 = "LRSTXH"
    test_2 = "OCEFXS"
    test_3 = "MXXXXX"


# -------------------------------------------------
class MarketSegmentID(str, Enum):
    """Código que identifica el segmento de mercado al que pertenece el instrumento."""

    ddf = "DDF"  # Instumentos de la División Derivados Financieros
    dda = "DDA"  # Instumentos de la División Derivados Agropecuarios
    dual = "DUAL"  # Instrumentos listados en DDF y DDA
    u_ddf = "U-DDF"
    u_dda = "U-DDA"
    u_dual = "U-DUAL"
    merv = "MERV"  # Instrumentos de mercados externos a Matba Rofex (Merval?)
    mae = "MAE"
    matba = "MATBA"
    mvr = "MVR"
    mvc = "MVC"
    mvm = "MVM"
    u_ddf_s = "U-DDF-S"
    u_fin = "U-FIN"
    u_comm = "U-COMM"
    u_stock = "U-STOCK"
    tiva = "TIVA"
    mfci = "MFCI"
    test = "TEST"  # Segmento de pruebas de Primary


# -------------------------------------------------
class MarketID(str, Enum):
    """Código que identifica el ID del mercado al que pertenece el segmento."""

    rofex = "ROFX"
    merval = "MERV"


# --------------------------------------------------
class InstrumentID(BaseModel):
    marketId: MarketID
    symbol: str


# -------------------------------------------------
class Entry(str, Enum):
    """Datos de mercado ques son posibles consultar por medio de las API tanto REST como WebSocket."""

    bid = "BI"
    offer = "OF"
    last = "LA"  # Ultimo precio
    open = "OP"  # Precio de apertura
    close = "CL"  # Precio de cierre ANTERIOR
    high = "HI"  # Precio máximo
    low = "LO"  # Precio mínimo
    trade_volume = "TV"  # Volumen operado en contratos/nominales (null value)
    settlement = "SE"  # Precio de ajuste (solo para futuros)
    open_interest = "OI"  # Interés abierto (solo para futuros)
    index_volue = "IV"  # Valor del índice (solo para índices)
    trade_effective_volume = "EV"  # Volumen efectivo de negociación
    nominal_volume = "NV"  # Volumen nominal de negociación
    auction_price = "ACP"  # Precio de cierre del día de la fecha para instrumentos externos a MATBA ROFEX


# -------------------------------------------------
class Depth(int, Enum):
    """Profundidad de mercado."""

    level_1 = 1  # Default value
    level_2 = 2
    level_3 = 3
    level_4 = 4
    level_5 = 5


# -------------------------------------------------
class SettlementTerm(str, Enum):
    t24 = "24hs"
    t48 = "48hs"
    t72 = "72hs"
    ci = "CI"


# -------------------------------------------------
class OrderType(str, Enum):
    """Tipo de orden."""

    limit = "LIMIT"
    market = "MARKET"
    stop_limit = "STOP_LIMIT"
    stop_limit_merval = "STOP_LIMIT_MERVAL"
    market_to_limit = "MARKET_TO_LIMIT"
    previously_quoted = "PREVIOUSLY_QUOTED"
    stop = "STOP"


# -------------------------------------------------
class OrderSide(str, Enum):
    """Dirección de la orden."""

    buy = "BUY"
    sell = "SELL"


# -------------------------------------------------
class OrderStatus(str, Enum):
    """Estado de la orden."""

    new = "NEW"
    pending_new = "PENDING_NEW"
    pending_replace = "PENDING_REPLACE"
    pending_cancel = "PENDING_CANCEL"
    rejected = "REJECTED"
    pending_approval = "PENDING_APPROVAL"
    canceled = "CANCELED"
    replaced = "REPLACED"


# -------------------------------------------------
class OrderTimeInForce(str, Enum):
    """Tiempo de vida de la orden."""

    day = "DAY"
    ioc = "IOC"  # Immediate or Cancel
    gtd = "GTD"  # Good Till Date
    fok = "FOK"  # Fill or Kill
    gtc = "GTC"


# -------------------------------------------------
class SyncResult(BaseModel):
    added: int
    deleted: int
    enviroment: Enviroment


# --------------------------------------------------
class PriceWithSize(BaseModel):
    price: float
    size: int


# --------------------------------------------------
class PriceWithSizeAndDate(PriceWithSize):
    size: Optional[int] = None  # Size of the last trade
    date: Optional[int] = None  # Timestamp in milliseconds since epoch


# --------------------------------------------------
class MarketData(BaseModel):
    nv: Optional[int] = None  # Notional Value
    bi: Optional[List[PriceWithSize]] = None  # Bid depends on the depth
    of: Optional[List[PriceWithSize]] = None  # Offer depends on the depth
    ev: Optional[float] = None  # Effective Value
    cl: Optional[PriceWithSizeAndDate] = None  # Previous Close
    la: Optional[PriceWithSizeAndDate] = None  # Last Trade
    op: Optional[float] = None  # Opening Price
    hi: Optional[float] = None  # Highest Price
    lo: Optional[float] = None  # Lowest Price
    tv: Optional[int] = None  # Volumen operado en contratos/nominales (null value)
    se: Optional[float] = None  # Precio de ajuste (solo para futuros)
    oi: Optional[float] = None  # Interés abierto (solo para futuros)
    iv: Optional[float] = None  # Valor del índice (solo para índices)
    acp: Optional[float] = (
        None  # Precio de cierre del día de la fecha para instrumentos externos a MATBA ROFEX
    )
