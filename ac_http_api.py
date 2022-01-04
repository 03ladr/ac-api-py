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
from fastapi import HTTPException, Depends, FastAPI, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from methods.fastapi.fastapi_config import oauth2_scheme
from methods.fastapi.fastapi_objects import Token, tags
# Item and User Modules
from methods.items import item_methods, item_objects
from methods.users import user_methods, user_objects
# Utilities
from datetime import datetime, timedelta
# Exception Objects
from methods.exceptions.exception_objects import *


""""DB INIT """
load_db()
""" WEB3 FILTER -> DATABASE POPULATION """
create_task(populate_db())
""" FASTAPI INIT """
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
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWTKEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(database: Session = Depends(get_db),
                           token: str = Depends(
                               oauth2_scheme)) -> user_objects.User:
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


async def get_operator(current_user: user_objects.User = Depends(
    get_current_user)) -> user_objects.User:
    """
    Gets user account and returns it if an operator
    """
    operator = user_methods.is_operator(contract, current_user)

    if not operator:
        raise HTTPException(status_code=403, detail="Not an operator account.")
    return current_user


""" ERROR HANDLING """


@app.exception_handler(PrivateKeyError)
async def badpkey_handler(request: Request, exc: PrivateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(OwnershipError)
async def notowner_handler(request: Request, exc: OwnershipError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NonExistentTokenError)
async def nonexist_handler(request: Request, exc: NonExistentTokenError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NotOperatorError)
async def notop_handler(request: Request, exc: NotOperatorError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NotClaimableError)
async def nonclaim_handler(request: Request, exc: NotClaimableError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(UnknownAccountError)
async def badacc_handler(request:  Request, exc: UnknownAccountError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


""" API METHODS """


@app.post("/users/create", response_model=user_objects.User, tags=[tags[0]])
async def create_user(
    user_obj: user_objects.UserBase, database: Session = Depends(get_db)
) -> user_objects.User:
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
            detail=f"Email has already been {user_obj.email} registered.")
    new_user = user_methods.create_user(database, w3, user_obj)
    return new_user


@app.get("/users/current", response_model=user_objects.User, tags=[tags[0]])
async def current_user_info(current_user: user_objects.User = Depends(
    get_current_user)) -> user_objects.User:
    """
    View account details of currently logged in user
    """
    return current_user


@app.get("/users/items/view", tags=[tags[0]])
async def view_items(current_user: user_objects.User = Depends(
    get_current_user), database: Session = Depends(get_db)) -> List:
    """
    View owned items of currently logged in user
    """
    owned_items = item_methods.get_user_items(database, TXReqs(),
                                              current_user.publickey.decode())
    if not owned_items:
        raise HTTPException(status_code=404, detail="No items found.")
    return owned_items


@app.post("/users/items/transfer", tags=[tags[0]])
async def transfer_item(
    item_id: int,
    receiver_attr: str,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user),
    database: Session = Depends(get_db)
) -> str:
    """
    Transfer item token
    """
    transferred_item = item_methods.transfer_item(
        database, TXReqs(privatekey=current_user.accesskey, passkey=passkey),
        item_id, receiver_attr)
    if not transferred_item:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return f"Item {item_id} transferred to user {receiver_attr}."


@app.get("/users/get/user={user_attr}",
         response_model=user_objects.UserDisplay,
         tags=[tags[0]])
def get_user(
    user_attr: str,
    database: Session = Depends(get_db),
    current_user: user_objects.User = Depends(get_current_user)
) -> user_objects.User:
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


@app.post("/items/create", tags=[tags[1]])
async def create_item(
    item_obj_list: List[item_objects.ItemCreate],
    passkey: str,
    current_operator: user_objects.User = Depends(get_operator)
) -> str:
    """
    Create item token
    """
    created_item = item_methods.create_item(
        ipfs, TXReqs(privatekey=current_operator.accesskey, passkey=passkey),
        item_obj_list)
    if not created_item:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return "Item created."


@app.post("/items/claim", tags=[tags[1]])
async def claim_item(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    Claim Item Token
    """
    item_methods.claim_item(
        TXReqs(privatekey=current_user.accesskey, passkey=passkey), item_id)
    return f"Item {item_id} has been claimed"


@app.post("/items/claimability/set", tags=[tags[1]])
async def toggle_item_claimability(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    Toggle item claimability
    """
    item_methods.set_item_claimability(
        TXReqs(privatekey=current_user.accesskey, passkey=passkey), item_id)
    return "Item claimability changed."


@app.post("/items/missing/set", tags=[tags[1]])
async def toggle_item_missing(
        item_id: int,
        database: Session = Depends(get_db),
        current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    Toggle item missing status
    """
    missing_status = item_methods.toggle_item_missing(database, TXReqs(), current_user, item_id)
    return f"{item_id} Missing Status: {missing_status}"


@app.post("/items/forfeit", tags=[tags[1]])
async def forfeit_item(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    Forfeit/burn Item Token
    """
    item_methods.burn_item_token(
        TXReqs(privatekey=current_user.accesskey, passkey=passkey), item_id)
    return f"Item {item_id} forfeited."


@app.get("/items/get/item={item_id}", tags=[tags[1]])
def get_item(item_id: int,
        database: Session = Depends(get_db)) -> item_objects.Item:
    """
    Display item token details by ID
    """
    item_obj = item_methods.get_item(database, TXReqs(), item_id)
    if item_obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_obj


@app.get("/items/claimability/view", tags=[tags[1]])
async def view_item_claimability(
    item_id: int, current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    View item claimability
    """
    item_claimability = item_methods.get_item_claimability(TXReqs(), item_id)
    return f"Item claimability status: {item_claimability}"


@app.post("/token", response_model=Token, tags=[tags[2]])
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
