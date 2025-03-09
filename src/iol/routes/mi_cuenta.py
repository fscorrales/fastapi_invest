# from fastapi import APIRouter

# from ..models import Rf602ValidationOutput
# from ..services import Rf602ServiceDependency

# rf602_router = APIRouter(prefix="/rf602", tags=["SIIF - rf602"])


# @rf602_router.post("/download_and_update/")
# async def siif_download(
#     ejercicio: str,
#     service: Rf602ServiceDependency,
# ) -> Rf602ValidationOutput:
#     return await service.download_and_update(ejercicio=ejercicio)
