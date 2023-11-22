from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.settings import ROUTE_PREFIX_V1
from core.dependencies import get_current_user,get_token_header

from . import fastapi_logs_mongodb

router = APIRouter(
        #dependencies=[Depends(get_current_user)]
        #dependencies=[Depends(get_token_header)]
    )

def include_api_routes():
    router.include_router(fastapi_logs_mongodb.router, prefix=ROUTE_PREFIX_V1)

include_api_routes()