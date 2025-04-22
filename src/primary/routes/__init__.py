__all__ = ["primary_router"]

from fastapi import APIRouter

from .segments import segments_router

# from .mi_cuenta_portafolio import mi_cuenta_portafolio_router
# from .titulos import titulos_router

primary_router = APIRouter(prefix="/primary")

primary_router.include_router(segments_router)
# primary_router.include_router(mi_cuenta_portafolio_router)
# primary_router.include_router(titulos_router)
