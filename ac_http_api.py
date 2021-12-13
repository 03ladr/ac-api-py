# Cryptography modules
from methods.crypto import aes_methods, sha_methods

# FastAPI
from fastapi import HTTPException, Depends, FastAPI, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Typing
from typing import Optional, List
from pydantic import BaseModel

# Web3 Connectivity
from web3 import Web3

# API/Database Connectivity/Tooling
import asyncio
import nest_asyncio
nest_asyncio.apply()
import uvloop
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from time import sleep

# Local modules
from methods.users import user_methods, user_objects
from methods.items import item_methods, item_objects
from methods.db import db_schemas
from methods.db.db import SessionLocal, engine
from methods.vars.strids import ItemID, UserID


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Creating DB tables
db_schemas.Base.metadata.create_all(bind=engine)


# Web3 Connectivity
# Currently using Arbitrum
w3 = Web3(
    Web3.HTTPProvider(
        "http://127.0.0.1:7545"
    )
)


# Database population from contract logs on blockchain init
# Check for streamlit docs . background loop
async def populate():
    print("test")
    asyncio.sleep(5)
loop = asyncio.get_event_loop()
try:
    loop.stop()
    sleep(3)
    loop.close()
except:
    pass
loop.create_task(populate())


# Json Web Token model
class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    id: str
    type: str


# JWT+Access key configuration
# JWT key generated with 'openssl rand -hex 32'
KEY = "8ed6f503a89743f17901e4be80491aba1a54cbf096446992c7566ce890317d97"
ACCKEY = sha_methods.create_hash("accesskey")

# FastAPI instantiation
app = FastAPI()

# OAuth Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Openapi tags
tags = (
    "User Methods",
    "Operator Methods",
    "Administrative Methods",
    "Utility Endpoints",
    "Item Verification",
)


## API FUNCTIONS ##


# Creating Json Web Token
def create_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm="HS256")
    return encoded_jwt


# Obtains current user from Json Web Token
async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        jwt_decoded = jwt.decode(token, KEY, algorithms=["HS256"])
        value = jwt_decoded.get("id")
        if value is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_methods.get_user_by(db, value)
    if user is None:
        raise credentials_exception
    return user


async def is_operator(current_user: user_objects.User = Depends(get_current_user)):
    if current_user.type == db_schemas.AccountType.operator:
        return current_user
    if current_user.type == db_schemas.AccountType.user:
        raise HTTPException(status_code=403, detail="Not an operator account.")


### API METHODS ###


## User Methods ##


# Account/User management
# Account creation
@app.post("/users/create", response_model=user_objects.UserDisplay, tags=[tags[0]])
async def create_user(user_obj: user_objects.UserBase, db: Session = Depends(get_db)):
    db_username = user_methods.get_user_by(db, user_obj.username)
    db_email = user_methods.get_user_by(db, user_obj.email)
    if db_username or db_email:
        raise HTTPException(
            status_code=400, detail="User already registered."
        )  # Find a different way to query existence
    created_user = user_methods.create_user(db, w3, user_obj)
    return created_user


# Get current logged in User object
@app.get("/users/current", response_model=user_objects.UserDisplay, tags=[tags[0]])
async def current_user(current_user: user_objects.User = Depends(get_current_user)):
    return current_user


# See owned items
@app.get("/users/items", response_model=List[item_objects.ItemDisplay], tags=[tags[0]])
async def view_items(current_user: user_objects.User = Depends(get_current_user)):
    items = current_user.items
    if not items:
        raise HTTPException(status_code=404, detail="No items found.")
    return items


# Transfer item
@app.post("/users/items", tags=[tags[0]])
async def transfer_item(
    itemid: ItemID,
    receiverid: UserID,
    current_user: user_objects.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inventory = [item.id for item in current_user.items]
    if itemid not in inventory:
        raise HTTPException(status_code=403, detail="Item not in inventory.")
    transferred = item_methods.transfer_item(db, itemid, receiverid)
    if not transferred:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return "Item {item} transferred to user {receiver}.".format(
        item=itemid, receiver=receiverid
    )


## Operator Methods ##


# Creating item
@app.post("/items/create", response_model=item_objects.ItemDisplay, tags=[tags[1]])
async def create_item(
    item_obj: item_objects.ItemCreate,
    operator: user_objects.User = Depends(is_operator),
    db: Session = Depends(get_db),
):
    db_item = item_methods.create_item(db, w3, item_obj, operator)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return db_item


## Verification Methods ##


@app.get("/items/verify/id={itemid}", tags=[tags[4]])
async def verify_item(itemid: ItemID, db: Session = Depends(get_db)):
    item = item_methods.get_item_by(db, itemid)
    if not item:
        raise HTTPException(status_code=404, detail="Item unknown/unauthenticated!")
    return "Item {itemid} is authentic. Owned by User: {userid}.".format(
        itemid=itemid, userid=item.owner_id
    )


## Administrative Methods ##


# Set account as operator by value (username, public key, id, email)
@app.post("/users/set", response_model=user_objects.UserDisplay, tags=[tags[2]])
async def set_operator(
    accesskey: str, user_attr: str, user_brand: str, db: Session = Depends(get_db)
):
    verified = sha_methods.verify_hash(accesskey, ACCKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")

    db_user = user_methods.set_operator(db, user_attr, user_brand)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user


# Display account details by value (username, public key, id, email)
@app.get(
    "/users/get/user={user_attr}", response_model=user_objects.User, tags=[tags[2]]
)
def get_user(accesskey: str, user_attr: str, db: Session = Depends(get_db)):
    verified = sha_methods.verify_hash(accesskey, ACCKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")
    db_user = user_methods.get_user_by(db, user_attr)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# List all users
@app.get("/users/get/all", response_model=List[user_objects.User], tags=[tags[2]])
def get_users(
    accesskey: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    verified = sha_methods.verify_hash(accesskey, ACCKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")

    db_users = user_methods.get_users(db, skip, limit)
    return db_users


# Display item details by value
@app.get("/items/get/item={itemid}", response_model=item_objects.Item, tags=[tags[2]])
def get_item(accesskey: str, itemid: ItemID, db: Session = Depends(get_db)):
    verified = sha_methods.verify_hash(accesskey, ACCKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")

    db_item = item_methods.get_item_by(db, itemid)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


# List all items
@app.get("/items/get/all", response_model=List[item_objects.Item], tags=[tags[2]])
def get_items(
    accesskey: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    verified = sha_methods.verify_hash(accesskey, ACCKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")

    db_items = item_methods.get_items(db, skip, limit)
    return db_items


## Utility Methods ##


# Create Json Web Token via+and user login
@app.post("/token", response_model=Token, tags=[tags[3]])
async def login_jwt_access(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = user_methods.verify_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    jwt_expiry = timedelta(minutes=30)
    access_token = create_jwt(data={"id": str(user.id)}, expires_delta=jwt_expiry)
    return {"access_token": access_token}

loop.run_forever()
