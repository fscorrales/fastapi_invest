__all__ = ["iol_router"]

from fastapi import APIRouter

from .mi_cuenta import mi_cuenta_router

# from .orders import orders_router

iol_router = APIRouter(prefix="/iol")

iol_router.include_router(mi_cuenta_router)
# siif_router.include_router(orders_router)
