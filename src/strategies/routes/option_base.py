# import os
# from typing import Annotated, List
# from fastapi import APIRouter, Depends, Query

from fastapi import APIRouter, Query

# from ...auth.services import OptionalAuthorizationDependency
# from ...config import settings
# from ...utils import RouteReturnSchema, apply_auto_filter, get_sqlite_path
# from ..schemas import Rvicon03Document, Rvicon03Filter, Rvicon03Params
from ..services import OptionBaseServiceDependency

option_base_router = APIRouter(
    prefix="/option_base", tags=["Strategies - Bases de Opciones"]
)


# -------------------------------------------------
@option_base_router.get(
    "/export",
    summary="Descarga la Listas de Opciones como archivo .xlsx",
    response_description="Archivo Excel con los registros solicitados",
    response_model=None,
)
async def export_all_from_db(
    service: OptionBaseServiceDependency,
    upload_to_google_sheets: bool = Query(False, alias="uploadToGoogleSheets"),
):
    return await service.export_all_from_db(
        upload_to_google_sheets=upload_to_google_sheets
    )
