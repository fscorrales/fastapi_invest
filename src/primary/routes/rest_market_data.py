from typing import Annotated, List

from fastapi import APIRouter, Depends

from ...auth.services import OptionalAuthorizationDependency
from ...config import logger
from ...utils import apply_auto_filter
from ..schemas import (
    PrimaryCredentials,
    RestMarketDataDocument,
    RestMarketDataFilter,
    RestMarketDataParams,
    SyncResult,
)
from ..services import (
    RestMarketDataServiceDependency,
    prepare_primary_credentials,
)

rest_market_data_router = APIRouter(
    prefix="/rest_maket_data", tags=["Primary - Rest Market Data"]
)


@rest_market_data_router.post("/sync_from_primary", response_model=SyncResult)
async def sync_rest_market_data_from_primary(
    auth: OptionalAuthorizationDependency,
    service: RestMarketDataServiceDependency,
    credentials: Annotated[PrimaryCredentials, Depends()],
    params: Annotated[RestMarketDataParams, Depends()],
):
    credentials = prepare_primary_credentials(auth, credentials)

    logger.info(
        f"Syncing {credentials.enviroment.value} instruments details from Primary API with url: {credentials.url}"
    )

    logger.info(f"Params: {params.model_dump(mode='json')}")

    return await service.sync_rest_market_data_from_primary(
        credentials=credentials,
        params=params,
    )


@rest_market_data_router.get(
    "/get_from_db", response_model=List[RestMarketDataDocument]
)
async def get_rest_market_data_from_db(
    service: RestMarketDataServiceDependency,
    params: Annotated[RestMarketDataFilter, Depends()],
):
    apply_auto_filter(params=params)
    return await service.get_rest_market_data_from_db(params=params)
