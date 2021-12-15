# Web3 Tooling 
from web3 import Web3
from methods.items.modules.abi import abi
from methods.items.item_filter import ItemFilters
# DB Tooling
import ipfshttpclient
from methods.db import db_schemas
from methods.db.db import SessionLocal, engine
# Typing
from pydantic import BaseModel
from typing import NamedTuple
# FastAPI
from fastapi.security import OAuth2PasswordBearer
# Other
import asyncio

### Web3 Configuration ###
CONTRACT_ADDRESS = "0xA5054259105a6b7D224b2aCa5675c21e8B0Eb77c"
w3 = Web3(
        Web3.HTTPProvider(
            "http://127.0.0.1:7545" # Ganache localhost
            )
        ) # Web3 Connectivity
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi) # Smart contract connection init
itemfilter = ItemFilters(SessionLocal(), contract) # Instantiating item filter
class TXSender(NamedTuple): # TX Send Object
    publickey: str
    privatekey: str
async def populate_db():
    # Contract event log -> database background process
    while True:
        itemfilter.filter()
        await asyncio.sleep(5)

### JWT Configuration ###
JWTKEY = "8ed6f503a89743f17901e4be80491aba1a54cbf096446992c7566ce890317d97" # openssl -rand 32
class Token(BaseModel):
    access_token: str
class TokenData(BaseModel):
    id: str
    type: str

### FastAPI Configuration ###
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESSKEY = "053930e3ff63ca4a4dc9633965855cbd919f2ba74dec820abf17f8bb28553fb7" # sha3-256 hash
tags = (
    "User Methods",
    "Operator Methods",
    "Administrative Methods",
    "Utility Endpoints",
    "Item Verification",
) # FastAPI visual tags

### Database Setup ###
def get_db(): # DB context manager
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_schemas.Base.metadata.create_all(bind=engine) # Create DB tables
ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001") # Connecting to IPFS
