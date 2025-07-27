from typing import List, Union

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..services import OptionBaseServiceDependency


# -------------------------------------------------
class ExportOptionsRequest(BaseModel):
    options_underlying: Union[List[str], str] = ["GGAL"]
    upload_to_google_sheets: bool = False


option_base_router = APIRouter(
    prefix="/option_base", tags=["Strategies - Bases de Opciones"]
)


# -------------------------------------------------
@option_base_router.post(
    "/export",
    summary="Descarga la Listas de Opciones como archivo .xlsx",
    response_description="Archivo Excel con los registros solicitados",
)
async def export_all_from_db(
    service: OptionBaseServiceDependency,
    options_underlying: Union[List[str], str] = ["GGAL"],
    upload_to_google_sheets: bool = Query(False, alias="uploadToGoogleSheets"),
):
    return await service.export_all_from_db(
        options_underlying=options_underlying,
        upload_to_google_sheets=upload_to_google_sheets,
    )
