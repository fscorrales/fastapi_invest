__all__ = ["primary_router"]

from fastapi import APIRouter

from .instruments import instruments_router
from .instruments_details import instruments_details_router
from .segments import segments_router

primary_router = APIRouter(prefix="/primary")

primary_router.include_router(segments_router)
primary_router.include_router(instruments_router)
primary_router.include_router(instruments_details_router)
