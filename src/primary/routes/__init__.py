__all__ = ["primary_router"]

from fastapi import APIRouter

from .instruments import instruments_router
from .instruments_by_cficode import instruments_by_cficode_router
from .instruments_by_segment import instruments_by_segment_router
from .instruments_details import instruments_details_router
from .rest_market_data import rest_market_data_router
from .segments import segments_router
from .ws_market_data import ws_market_data_router

primary_router = APIRouter(prefix="/primary")

primary_router.include_router(segments_router)
primary_router.include_router(instruments_router)
primary_router.include_router(instruments_details_router)
primary_router.include_router(instruments_by_segment_router)
primary_router.include_router(instruments_by_cficode_router)
primary_router.include_router(rest_market_data_router)
primary_router.include_router(ws_market_data_router)
