# Cryptography modules
from methods.crypto import aes_methods, sha_methods
# FastAPI
from fastapi import HTTPException, Depends, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm
# Typing
from typing import Optional, List
# API/Database Connectivity/Tooling
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
# Local modules
from ac_api_config import *
from methods.items import item_methods, item_objects
from methods.users import user_methods, user_objects

### WEB3 FILTER -> DB POPULATION ###
asyncio.create_task(populate_db())

### FASTAPI INIT ###
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
    user = user_methods.get_user_by(db, value)
    if user is None:
        raise credentials_exception
    return user

# Checks if user is operator
async def is_operator(current_user: user_objects.User = Depends(get_current_user)):    
    isoperator = user_methods.is_operator(contract, current_user)
    if not isoperator:
        raise HTTPException(status_code=403, detail="Not an operator account.")
    return isoperator

# Grants/denies admin access
async def admin_access(accesskey: str):
    verified = sha_methods.verify_hash(accesskey, ACCESSKEY)
    if not verified:
        raise HTTPException(status_code=403, detail="Access denied.")
    return verified

# Creates transaction tuple
async def send_tx(user, accesskey):
    privatekey = aes_methods.aes_decrypt(user.accesskey, accesskey)
    return TXSender(publickey=user.publickey, privatekey=privatekey) 

### API METHODS ###
## User Methods ##
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
@app.get("/users/items", response_model=List[item_objects.Item], tags=[tags[0]])
async def view_items(current_user: user_objects.User = Depends(get_current_user)):
    items = current_user.items
    if not items:
        raise HTTPException(status_code=404, detail="No items found.")
    return items

# Transfer item
@app.post("/users/items", tags=[tags[0]])
async def transfer_item(
    itemid: int,
    receiver: user_objects.UserID,
    current_user: user_objects.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transferred = item_methods.transfer_item(db, w3, contract, itemid, receiver, send_tx(current_user, accesskey))
    if not transferred:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return "Item {item} transferred to user {receiver}.".format(
        item=itemid, receiver=receiverid
    )

## Operator Methods ##
# Creating item
@app.post("/items/create", tags=[tags[1]])
async def create_item(
    item_obj: item_objects.ItemCreate,
    operator: user_objects.User = Depends(is_operator),
    db: Session = Depends(get_db),
):
    itemid = item_methods.create_item(contract, ipfs, item_obj, operator.publickey)
    if not itemid:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return "Item created."

## Verification Methods ##
# Verifying item
@app.get("/items/verify/id={itemid}", tags=[tags[4]])
async def verify_item(itemid: int, db: Session = Depends(get_db)):
    item = item_methods.get_item(db, itemid)
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
@app.get("/items/get/item={itemid}", response_model=item_objects.Item, tags=[tags[2]])
def get_item(accesskey: str, itemid: int, db: Session = Depends(get_db)):
    admin_access(accesskey)

    db_item = item_methods.get_item(db, itemid)
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
    access_token = create_jwt(data={"id": str(user.id)}, expires_delta=jwt_expiry)
    return {"access_token": access_token}
