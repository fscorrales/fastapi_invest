__all__ = ["rava_router"]

from fastapi import APIRouter

from .bonds import bonds_router

rava_router = APIRouter(prefix="/rava")

rava_router.include_router(bonds_router)
