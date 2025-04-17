__all__ = ["iol_router"]

from fastapi import APIRouter

from .mi_cuenta_estado import mi_cuenta_estado_router
from .mi_cuenta_portafolio import mi_cuenta_portafolio_router
from .titulos import titulos_router

iol_router = APIRouter(prefix="/iol")

iol_router.include_router(mi_cuenta_estado_router)
iol_router.include_router(mi_cuenta_portafolio_router)
iol_router.include_router(titulos_router)
