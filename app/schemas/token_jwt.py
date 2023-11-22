from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    client_name: str | None = "ofm"
    client_secret: str | None = "6e79770a20e5c06cff4c895821161d0ff6cb1c71a9c8d631f374704cdfe1601c"
    client_type: int | None = 1
    disabled: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    client_name: str | None = None