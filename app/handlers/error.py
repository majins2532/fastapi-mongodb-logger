from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
import requests, json
from core.dependencies import set_http_error

async def http_error_handler(request: Request, exc: HTTPException):
    ''' Customize response when HTTPException '''
    print("HTTPException",dir(exc),dir(request))
    # send_to_mongodb(exc.status_code, request.method, exc.detail, request.scope.get("path"), None)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    ''' Customize response when RequestValidationError '''
    print("RequestValidationError")
    err_val = exc.errors()[0]
    err_type = err_val.get("type").split(".")[0]
    if err_type == "value_error":
        err_code = "E102"
    elif err_type == "type_error":
        err_code = "E103"
    error = {
                "status": "Fail",
                "error_code": err_code,
                "massage": {
                    "type": err_val.get("type"),
                    "msg": err_val.get("msg"),
                    "field": err_val.get('loc')
                },
                "custom_msg": {}
            }
    return JSONResponse(status_code=422,content=error)

async def server_exceptions_handler(request: Request, exc: Exception):
    ''' Customize response when Exception '''
    print("Exception",dir(exc),dir(request))
    # send_to_mongodb(500, request.method, str(exc), str(request.url), None)
    return JSONResponse(status_code=500, content=set_http_error("E999","",str(exc)))

async def requests_http_error_exceptions_handler(request: Request, exc: requests.exceptions.HTTPError):
    ''' Customize response when Exception '''
    print("requests.exceptions.HTTPError",dir(exc),dir(request))
    err_data = {
        "out": json.loads(exc.request.body),
        "in": exc.response.text,
    }
    # send_to_mongodb(exc.response.status_code, exc.request.method, err_data, exc.request.url, None)
    return JSONResponse(status_code=exc.response.status_code, content=set_http_error("E201","",err_data))

async def requests_connection_error_exceptions_handler(request: Request, exc: requests.exceptions.ConnectionError):
    ''' Customize response when Exception '''
    print("requests.exceptions.ConnectionError",dir(exc))
    # err_data = {
    #     "out": json.loads(exc.request.body),
    #     "in": json.loads(exc.response.text),
    # }
    # send_to_mongodb(exc.response.status_code, exc.request.method, json.loads(exc.response.text), exc.request.url, None)
    return JSONResponse(status_code=exc.response.status_code, content=set_http_error("E203","",json.loads(exc.response.text)))

async def requests_timeout_error_exceptions_handler(request: Request, exc: requests.exceptions.Timeout):
    ''' Customize response when Exception '''
    print("requests.exceptions.Timeout",dir(exc))
    #err_data = {
    #    "out": json.loads(exc.request.body),
    #    "in": json.loads(exc.response.text),
    #}
    # send_to_mongodb(exc.response.status_code, exc.request.method, json.loads(exc.response.text), exc.request.url, None)
    return JSONResponse(status_code=exc.response.status_code, content=set_http_error("E204","",json.loads(exc.response.text)))