# Configuration Variables
from ac_api_config import JWTKEY, ACCESSKEY
# Cryptography modules
from methods.cryptography import sha_methods
# Typing
from typing import Optional, List
# Database Connectivity/Tooling
from asyncio import create_task
from sqlalchemy.orm import Session
from methods.database.db import ipfs
from methods.database.db_methods import load_db, populate_db, get_db
# On-Chain Connectivity/Tooling
from methods.onchain.onchain_config import w3, contract
from methods.onchain.onchain_objects import TXReqs
# FastAPI Dependencies/Tooling
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm
from methods.fastapi.fastapi_config import oauth2_scheme
from methods.fastapi.fastapi_objects import Token, TokenData, fastapi_tags
# Item and User Modules
from methods.items import item_methods, item_objects
from methods.users import user_methods, user_objects
# Utilities
from datetime import datetime, timedelta

### DB INIT ###
load_db()
### WEB3 FILTER -> DB POPULATION ###
create_task(populate_db())

### FASTAPI INIT ###
tags = fastapi_tags # Don't ask
app = FastAPI()

### API FUNCTIONS ###
# Creating Json Web Token
def create_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWTKEY, algorithm="HS256")
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
        jwt_decoded = jwt.decode(token, JWTKEY, algorithms=["HS256"])
        value = jwt_decoded.get("id")
        if value is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    db_user = user_methods.get_user_by(db, value)
    if db_user is None:
        raise credentials_exception
    return db_user

# Checks if user is operator
async def get_operator(current_user: user_objects.User = Depends(get_current_user)):
    operator = user_methods.is_operator(contract, current_user)
    if not operator:
        raise HTTPException(status_code=403, detail="Not an operator account.")
    return operator

# Grants/denies admin access
def admin_access(accesskey: str):
    admin_bool = sha_methods.verify_hash(accesskey, ACCESSKEY)
    if not admin_bool:
        raise HTTPException(status_code=403, detail="Access denied.")
    return admin_bool

### API METHODS ###
## User Methods ##
# Account creation
@app.post("/users/create", response_model=user_objects.User, tags=[tags[0]])
async def create_user(user_obj: user_objects.UserBase, db: Session = Depends(get_db)):
    db_username = user_methods.get_user_by(db, user_obj.username)
    db_email = user_methods.get_user_by(db, user_obj.email)
    if db_username:
        raise HTTPException(status_code=400, detail="Username {username} has already been registered.".format(username=user_obj.username))
    elif db_email:
        raise HTTPException(status_code=400, detail="Email {email} registered.".format(email=user_obj.email))
    new_user = user_methods.create_user(db, w3, user_obj)
    return new_user

# Get current logged in User object
@app.get("/users/current", response_model=user_objects.User, tags=[tags[0]])
async def current_user(current_user: user_objects.User = Depends(get_current_user)):
    return current_user

# See owned items
@app.get("/users/items", tags=[tags[0]])
async def view_items(current_user: user_objects.User = Depends(get_current_user)):
    #db_items = current_user.items
    db_items = "notImplemented"
    if not db_items:
        raise HTTPException(status_code=404, detail="No items found.")
    return db_items

# Transfer item
@app.post("/users/items/transfer", tags=[tags[0]])
async def transfer_item(
    item_id: int,
    receiver_id: user_objects.UserID,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transferred_item = item_methods.transfer_item(
            item_id, user_methods.get_user_publickey(db, receiver_id), TXReqs(
                privatekey=current_user.accesskey, 
                passkey=passkey
            )
        )
    if not transferred_item:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return "Item {item} transferred to user {receiver}.".format(
        item=item_id, receiver=receiver_id
    )

## Operator Methods ##
# Creating item
@app.post("/items/create", tags=[tags[1]])
async def create_item(
    item_obj: item_objects.ItemCreate,
    passkey: str,
    current_operator: user_objects.User = Depends(get_operator),
    db: Session = Depends(get_db)
):
    created_item = item_methods.create_item(
            ipfs, item_obj, TXReqs(
                privatekey=current_operator.accesskey,
                passkey=passkey
            )
        )
    if not created_item:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return "Item created."

## Verification Methods ##
# Verifying item
@app.get("/items/verify/id={itemid}", tags=[tags[4]])
async def verify_item(item_id: int, db: Session = Depends(get_db)):
    item_obj = item_methods.get_item(db, item_id)
    if not item_obj:
        raise HTTPException(
            status_code=404, detail="Item unknown/unauthenticated!")
    return "Item {itemid} is authentic. Owned by User: {userid}.".format(
        itemid=item_id, userid=item_obj.owner_id
    )

## Administrative Methods ##
# Set account as operator by value (username, public key, id, email)
@app.post("/users/set", response_model=user_objects.User, tags=[tags[2]])
async def set_operator(
    accesskey: str, user_attr: str, user_brand: str, db: Session = Depends(get_db)
):    
    admin_access(accesskey)

    db_user = user_methods.set_operator(db, contract, user_attr, user_brand)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

# Display account details by value (username/public key/id/email)
@app.get(
    "/users/get/user={user_attr}", response_model=user_objects.User, tags=[tags[2]]
)
def get_user(user_attr: str, accesskey: str, db: Session = Depends(get_db)):
    admin_access(accesskey)

    db_user = user_methods.get_user_by(db, user_attr)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# List all users
@app.get("/users/get/all", response_model=List[user_objects.User], tags=[tags[2]])
def get_users(
    accesskey: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    admin_access(accesskey)

    db_users = user_methods.get_users(db, skip, limit)
    return db_users

# Display item details by value
@app.get("/items/get/item={itemid}", tags=[tags[2]])
def get_item(accesskey: str, item_id: int, db: Session = Depends(get_db)):
    admin_access(accesskey)

    db_item = item_methods.get_item(db, TXReqs(), item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# List all items
@app.get("/items/get/all", response_model=List[item_objects.Item], tags=[tags[2]])
def get_items(
    accesskey: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    admin_access(accesskey)

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
    access_token = create_jwt(
        data={"id": str(user.id)}, expires_delta=jwt_expiry)
    return {"access_token": access_token}
