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
from methods.database.database import ipfs
from methods.database.db_methods import load_db, populate_db, get_db
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
def create_jwt(data: dict, expires_delta: Optional[timedelta] = None) -> str:
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
                           token: str = Depends(oauth2_scheme)) -> user_objects.User:
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
        current_user: user_objects.User = Depends(get_current_user)) -> user_objects.User:
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
                      database: Session = Depends(get_db)) -> user_objects.User:
    """
    Create user account
    """
    db_username = user_methods.get_user_by(database, user_obj.username)
    db_email = user_methods.get_user_by(database, user_obj.email)
    if db_username:
        raise HTTPException(
            status_code=400,
            detail=f"Username {user_obj.username} has already been registered."
        )
    if db_email:
        raise HTTPException(
            status_code=400,
            detail=f"Email {user_obj.email} registered.")
    new_user = user_methods.create_user(database, w3, user_obj)
    return new_user


@app.get("/users/current", response_model=user_objects.User, tags=[tags[0]])
async def current_user_info(
        current_user: user_objects.User = Depends(get_current_user)) -> user_objects.User:
    """
    View account details of currently logged in user
    """
    return current_user


@app.get("/users/items", tags=[tags[0]])
async def view_items(
        current_user: user_objects.User = Depends(get_current_user)) -> List:
    """
    View owned items of currently logged in user
    """
    owned_items = item_methods.get_user_items(TXReqs(),
                                              current_user.publickey.decode())
    if not owned_items:
        raise HTTPException(status_code=404, detail="No items found.")
    return owned_items


@app.post("/items/transfer", tags=[tags[0]])
async def transfer_item(
        item_id: int,
        receiver_id: user_objects.UserID,
        passkey: str,
        current_user: user_objects.User = Depends(get_current_user),
        database: Session = Depends(get_db),
) -> str:
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
    return f"Item {item_id} transferred to user {receiver_id}."


# Display account details by value (username/public key/id/email)
@app.get("/users/get/user={user_attr}",
         response_model=user_objects.User,
         tags=[tags[2]])
def get_user(user_attr: str, database: Session = Depends(get_db)) -> user_objects.User:
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


@app.get("/items/info/item={itemid}", tags=[tags[2]])
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
) -> str:
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
async def verify_item(item_id: int, database: Session = Depends(get_db)) -> str:
    """
    Verify item token
    """
    item_obj = item_methods.get_item(database, TXReqs(), item_id)
    if not item_obj:
        raise HTTPException(status_code=404,
                            detail="Item unknown/unauthenticated!")
    return f"Item {item_id} is authentic."


@app.get("/items/info/claimability")
async def view_item_claimability(item_id: int,
                                current_user: user_objects.User = Depends(get_current_user)) -> str:
    item_claimability = item_methods.get_item_claimability(TXReqs(), itemid)
    return f"Item claimability status: {item_claimability}"


@app.get("/items/info/claimability")
async def toggle_item_claimability(item_id: int, passkey: str,
                                current_user: user_objects.User = Depends(get_current_user)) -> str:
    item_claimability = item_methods.set_item_claimability(TXReqs(privatekey=current_user.privatekey, passkey=passkey), itemid)
    return f"Item claimability status: {item_claimability}"


@app.get("/items/info/transfercount")
async def view_item_transfercount(item_id: int, db: Session = Depends(get_db),
                                current_user: user_objects.User = Depends(get_current_user)) -> str:
    item_claimability = item_methods.get_item_transfercount(db, itemid)
    return f"Item transfer ciunt: {item_claimability}"


@app.post("/token", response_model=Token, tags=[tags[3]])
async def login_jwt_access(form_data: OAuth2PasswordRequestForm = Depends(),
                           database: Session = Depends(get_db)) -> dict:
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
