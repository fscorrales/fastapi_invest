__all__ = ["Comisiones", "DerechosDeMercado", "GastosConIVA"]

from enum import Enum


# -------------------------------------------------
class Comisiones(float, Enum):
    """Commission rates applied to different financial instruments, expressed as decimal percentages.
    These rates are used to calculate the transaction commission or fees charged by the market or broker,
    depending on the instrument and operation type."""

    accion = 0.0015
    cedear = 0.0015
    opcion = 0.0015
    bono = 0.0015
    on = 0.0015
    letra = 0.0015
    caucion_pesos_colocador = 0.015  # anual (monto_final × 0,015 ÷ 365 × dias)
    caucion_pesos_tomador = 0.03  # anual (monto_final × 0,03 ÷ 365 × dias)
    caucion_dolar_colocador = 0.002  # anual (monto_final × 0,002 ÷ 365 × dias)
    caucion_dolar_tomador = 0.01  # anual (monto_final × 0,01 ÷ 365 × dias)


# -------------------------------------------------
class DerechosDeMercado(float, Enum):
    """Market rights fee rates for each type of financial instrument, expressed as a decimal percentage.
    These rates are used to calculate the regulatory fee applied to trades according to the instrument type."""

    accion = 0.0008
    cedear = 0.0008
    bono = 0.001  # sin IVA
    opcion = 0.002
    on = 0.0001  # sin IVA
    letra = 0.002  # sin IVA
    caucion = (
        0.0018  # 0,045% prorrateados c/ 90 días. (monto_final × 0,0018 ÷ 360 × dias)
    )


# -------------------------------------------------
class GastosConIVA:
    """Gastos totales con IVA incluidos, según tipo de instrumento."""

    accion = (Comisiones.accion.value + DerechosDeMercado.accion.value) * 1.21
    cedear = (Comisiones.cedear.value + DerechosDeMercado.cedear.value) * 1.21
    opcion = (Comisiones.opcion.value + DerechosDeMercado.opcion.value) * 1.21
    bono = Comisiones.bono.value + DerechosDeMercado.bono.value
    on = Comisiones.on.value + DerechosDeMercado.on.value
    letra = Comisiones.letra.value + DerechosDeMercado.letra.value

    caucion_pesos_colocador = round(
        (Comisiones.caucion_pesos_colocador.value + DerechosDeMercado.caucion.value)
        * 1.21,
        3,
    )
    caucion_pesos_tomador = round(
        (Comisiones.caucion_pesos_tomador.value + DerechosDeMercado.caucion.value)
        * 1.21,
        3,
    )
    caucion_dolar_colocador = round(
        (Comisiones.caucion_dolar_colocador.value + DerechosDeMercado.caucion.value)
        * 1.21,
        3,
    )
    caucion_dolar_tomador = round(
        (Comisiones.caucion_dolar_tomador.value + DerechosDeMercado.caucion.value)
        * 1.21,
        3,
    )
