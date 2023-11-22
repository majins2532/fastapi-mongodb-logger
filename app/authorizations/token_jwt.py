from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

# Set Token JWT
# to get a string like this run:
# openssl rand -hex 32
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, USER_API, SECRET_KEY, ALGORITHM
from schemas.token_jwt import Token, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["OAuth2"])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    data["hashed_password"] = ""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt =  jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, client_name: str):
    if client_name in db:
        user_dict = db[client_name]
        return User(**user_dict)
    
def authenticate_user(fake_db, client_name: str, client_secret: str):
    user = get_user(fake_db, client_name)
    if not user:
        return False
    if user.disabled:
        return False
    if not verify_password(client_secret, user.client_secret):
        return False
    return user

@router.post("/v1/OAuth2/token", response_model=Token)
async def login_get_access_token(form_data: User):
    user = authenticate_user(USER_API, form_data.client_name, form_data.client_secret)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_name",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.client_name}, expires_delta=access_token_expires
    )
    if user.client_type == 1:
        token_type = "bearer"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect client_type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": token_type}