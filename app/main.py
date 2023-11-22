from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import fastapi.exceptions
from core.settings import TAGS_METADATA, DESCRIPTION, MAIN_API_PREFIX, VERSION, TERMS, TITLE, MAIN_API_PREFIX, ROUTE_PREFIX_V1
from core.dependencies import get_token_header
from fastapi.responses import HTMLResponse, RedirectResponse

from authorizations.token_jwt import router as router_auth
from routers.api_control import router as router_control

import requests
from handlers.error import http_error_handler,validation_exception_handler,requests_http_error_exceptions_handler, server_exceptions_handler, requests_connection_error_exceptions_handler, requests_timeout_error_exceptions_handler

def get_application():

    ## Start FastApi App 
    application = FastAPI(
        openapi_tags=TAGS_METADATA,
        redoc_url=None,
        version=VERSION,
        terms_of_service=TERMS,
        title=TITLE,
        #responses=ERROR_RESPONSES,
        description=DESCRIPTION,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        #dependencies=[Depends(get_token_header)]
    )

    ## Mapping api routes
    application.include_router(router_control, prefix=MAIN_API_PREFIX)
    ## Mapping api Auth
    application.include_router(router_auth, prefix=MAIN_API_PREFIX)

    ## Add exception handlers
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, server_exceptions_handler)
    application.add_exception_handler(requests.exceptions.HTTPError, requests_http_error_exceptions_handler)
    application.add_exception_handler(requests.exceptions.ConnectionError, requests_connection_error_exceptions_handler)
    application.add_exception_handler(requests.exceptions.Timeout, requests_timeout_error_exceptions_handler)

    # ## Allow cors
    # application.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=ALLOWED_HOSTS or ["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )
    
    return application

app = get_application()

@app.get("/api/v1/check_connect", tags=["Check"], status_code=200)
async def check_connect_odoo():
    res = odoo.version_odoo()
    return res

@app.get("/")
async def root():
    PATH_API = f"{MAIN_API_PREFIX}{ROUTE_PREFIX_V1}"
    return RedirectResponse(url=PATH_API+"/nf_login", status_code=303)
    #return {"message": "Hello Bigger Applications!"}