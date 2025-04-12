__all__ = ["iol_router"]

from fastapi import APIRouter

from .mi_cuenta import mi_cuenta_router
from .titulos import titulos_router

iol_router = APIRouter(prefix="/iol")

iol_router.include_router(mi_cuenta_router)
iol_router.include_router(titulos_router)
