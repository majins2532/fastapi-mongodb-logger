import datetime, json, requests
from fastapi import Header, HTTPException, Depends
from fastapi.security import APIKeyHeader,HTTPAuthorizationCredentials,HTTPBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

# import schemas
from core.settings import API_TOKEN_KEY, MDB_DATABASE
from core.mdbutils import mdb_connection

header_scheme = APIKeyHeader(name="api-token-key")
security = HTTPBearer()

def set_http_error(err_code, str_th, str_en):
    return {
        "status": "Fail",
        "massage": {
            "massage_th":f"{str_th}",
            "massage_en":f"{str_en}"
        },
        "error_code": err_code
    }

async def get_token_header(api_token_key: str = Depends(header_scheme)):
    if api_token_key != API_TOKEN_KEY:
        raise HTTPException(status_code=401, 
            detail=set_http_error("E101","API-TOKEN-KEY ไม่ถูกต้อง", "Invalid api_token_key"))
    
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail=set_http_error("E101","ไม่สามารถตรวจสอบข้อมูลรับรองได้", "Could not validate credentials."),
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_name = payload.get("sub")
        if client_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = USER_API.get(client_name, None)
    if user is None:
        raise credentials_exception
    if user.get("disabled"):
        raise HTTPException(status_code=400, detail=set_http_error("E101","ลูกค้ารายนี้ไม่อนุญาตให้เข้าถึง", "This client does not allow access."))
    return True

mdb = mdb_connection()
mdb.connect(MDB_DATABASE)
if mdb.is_connect:
    print("\033[1;32;40m Connect MongoDB Database [fastapi][logs] True <<<<<< DONE")
else:
    print("\033[1;31;40m Connect MongoDB Database [fastapi][logs] False <<<<<< Fail")

print("\033[0m")