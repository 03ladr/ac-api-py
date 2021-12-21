"""
Authentichain HTTP API
FastAPI-Based
"""
# Configuration Variables
from config import JWTKEY
# Typing
from typing import Optional, List
# Database Connectivity/Tooling
from asyncio import create_task
from sqlalchemy.orm import Session
from methods.db.database import ipfs
from methods.db.db_methods import load_db, populate_db, get_db
# On-Chain Connectivity/Tooling
from methods.onchain.onchain_config import w3, contract
from methods.onchain.onchain_objects import TXReqs
# FastAPI Dependencies/Tooling
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm
from methods.fastapi.fastapi_config import oauth2_scheme
from methods.fastapi.fastapi_objects import Token, tags
# Item and User Modules
from methods.items import item_methods, item_objects
from methods.users import user_methods, user_objects
# Utilities
from datetime import datetime, timedelta


""""DB INIT """
load_db()
""" WEB3 FILTER -> database POPULATION """
create_task(populate_db())
"""## FASTAPI INIT """
app = FastAPI()


""" API FUNCTIONS """
def create_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create Json Web Token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWTKEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(database: Session = Depends(get_db),
                           token: str = Depends(oauth2_scheme)):
    """
    Obtains details of currently logged in user
    """
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
    db_user = user_methods.get_user_by(database, value)
    if db_user is None:
        raise credentials_exception
    return db_user


async def get_operator(
        current_user: user_objects.User = Depends(get_current_user)):
    """
    Gets user account and returns it if an operator
    """
    operator = user_methods.is_operator(contract, current_user)
    if not operator:
        raise HTTPException(status_code=403, detail="Not an operator account.")
    return operator


""" API METHODS """
@app.post("/users/create", response_model=user_objects.User, tags=[tags[0]])
async def create_user(user_obj: user_objects.UserBase,
                      database: Session = Depends(get_db)):
    """
    Create user account
    """
    db_username = user_methods.get_user_by(database, user_obj.username)
    db_email = user_methods.get_user_by(database, user_obj.email)
    if db_username:
        raise HTTPException(
            status_code=400,
            detail="Username {username} has already been registered.".format(
                username=user_obj.username),
        )
    if db_email:
        raise HTTPException(
            status_code=400,
            detail="Email {email} registered.".format(email=user_obj.email),
        )
    new_user = user_methods.create_user(database, w3, user_obj)
    return new_user


@app.get("/users/current", response_model=user_objects.User, tags=[tags[0]])
async def current_user_info(
        current_user: user_objects.User = Depends(get_current_user)):
    """
    View account details of currently logged in user
    """
    return current_user


@app.get("/users/items", tags=[tags[0]])
async def view_items(
        current_user: user_objects.User = Depends(get_current_user)):
    """
    View owned items of currently logged in user
    """
    owned_items = item_methods.get_user_items(TXReqs(),
                                              current_user.publickey.decode())
    if not owned_items:
        raise HTTPException(status_code=404, detail="No items found.")
    return owned_items


@app.post("/users/items/transfer", tags=[tags[0]])
async def transfer_item(
        item_id: int,
        receiver_id: user_objects.UserID,
        passkey: str,
        current_user: user_objects.User = Depends(get_current_user),
        database: Session = Depends(get_db),
):
    """
    Transfer item token
    """
    transferred_item = item_methods.transfer_item(
        item_id,
        user_methods.get_user_publickey(database, receiver_id),
        TXReqs(privatekey=current_user.accesskey, passkey=passkey),
    )
    if not transferred_item:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return "Item {item} transferred to user {receiver}.".format(
        item=item_id, receiver=receiver_id)


# Display account details by value (username/public key/id/email)
@app.get("/users/get/user={user_attr}",
         response_model=user_objects.User,
         tags=[tags[2]])
def get_user(user_attr: str, database: Session = Depends(get_db)):
    """
    Display account details by value
    Acccepted queries:
        - username
        - public key
        - user ID
        - e-mail
    """
    db_user = user_methods.get_user_by(database, user_attr)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/items/get/item={itemid}", tags=[tags[2]])
def get_item(item_id: int, database: Session = Depends(get_db)):
    """
    Display item token details by ID
    """
    item_obj = item_methods.get_item(database, TXReqs(), item_id)
    if item_obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_obj


@app.post("/items/create", tags=[tags[1]])
async def create_item(
        item_obj: item_objects.ItemCreate,
        passkey: str,
        current_operator: user_objects.User = Depends(get_operator)
):
    """
    Create item token
    """
    created_item = item_methods.create_item(
        ipfs, item_obj,
        TXReqs(privatekey=current_operator.accesskey, passkey=passkey))
    if not created_item:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return "Item created."


@app.get("/items/verify/id={itemid}", tags=[tags[4]])
async def verify_item(item_id: int, database: Session = Depends(get_db)):
    """
    Verify item token
    """
    item_obj = item_methods.get_item(database, item_id)
    if not item_obj:
        raise HTTPException(status_code=404,
                            detail="Item unknown/unauthenticated!")
    return "Item {itemid} is authentic. Owned by User: {userid}.".format(
        itemid=item_id, userid=item_obj.owner_id)


@app.post("/token", response_model=Token, tags=[tags[3]])
async def login_jwt_access(form_data: OAuth2PasswordRequestForm = Depends(),
                           database: Session = Depends(get_db)):
    """
    Create Json Web Token via+and user login
    """
    user = user_methods.verify_user(database, form_data.username,
                                    form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    jwt_expiry = timedelta(minutes=30)
    access_token = create_jwt(data={"id": str(user.id)},
                              expires_delta=jwt_expiry)
    return {"access_token": access_token}
