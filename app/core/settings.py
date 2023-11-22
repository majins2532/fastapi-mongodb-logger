from dotenv import load_dotenv
import os

load_dotenv('.config.env')

## Config Base
VERSION = os.getenv('VERSION')
TERMS = os.getenv('TERMS')
TITLE = os.getenv('TITLE')
API_TOKEN_KEY = os.getenv('API_TOKEN_KEY')
MAIN_API_PREFIX = os.getenv('MAIN_API_PREFIX')
ROUTE_PREFIX_V1 = os.getenv('ROUTE_PREFIX_V1')
MDB_DATABASE = os.getenv("MDB_DATABASE")
## Auth
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 0
USER_API = {
    "ofm": {
        "client_name": "ofm",
        "client_secret": pwd_context.hash("6e79770a20e5c06cff4c895821161d0ff6cb1c71a9c8d631f374704cdfe1601c"),
        "client_type": 1,
        "disabled": False,
    }
}
SECRET_KEY = "20b99e47adff34058007e61bcafe34d37c2eb84b4acbd0e408e7c9ffd97ff683"
ALGORITHM = "HS256"

## Config MongoDB
MDB_USERNAME = os.getenv('MDB_USERNAME')
MDB_PASSWORD =os.getenv('MDB_PASSWORD')
MDB_HOST = os.getenv('MDB_HOST')
MDB_PORT = os.getenv('MDB_PORT')

# Token Client From OFM
TOKEN_CLIENT_OFM = {
    "token_client": None,
    "token_type": None,
    "api_key": os.getenv('ofm_api_key')
}
# Default FastAPI
TAGS_METADATA = [
    {
        "name": "Check",
        "description": "Check Server Connect to Odoo MP",
    },
]
DESCRIPTION = f"""
Netforce Logger By MongoDB API APP helps you do awesome stuff. 🚀

## API-TOKEN-KEY

You can **API-TOKEN-KEY** : {API_TOKEN_KEY}
"""