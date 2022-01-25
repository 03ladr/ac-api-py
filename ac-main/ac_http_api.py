"""
Authentichain HTTP API
FastAPI-Based
"""
from asyncio import create_task
from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, load_only

from methods.database import db_schemas
from methods.database.database import ipfs
from methods.database.db_methods import get_db, load_db, populate_db
from methods.exceptions.exception_objects import (
    NonExistentTokenError,
    NotClaimableError,
    NotOperatorError,
    OwnershipError,
    PrivateKeyError,
    UnknownAccountError,
)
from methods.fastapi.fastapi_methods import create_jwt, get_current_user
from methods.fastapi.fastapi_objects import Token, tags
from methods.items import item_methods, item_objects
from methods.onchain.onchain_config import w3
from methods.onchain.onchain_methods import (
    build_item_call,
    build_item_tx,
    build_mint_tx,
)
from methods.users import user_methods, user_objects


# Initialization
""" DB INIT """
load_db()
""" WEB3 FILTER -> DATABASE POPULATION """
create_task(populate_db())
""" FASTAPI INIT """
app = FastAPI()


# Error Handling
@app.exception_handler(PrivateKeyError)
async def badpkey_handler(request: Request,
                          exc: PrivateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(OwnershipError)
async def notowner_handler(request: Request,
                           exc: OwnershipError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NonExistentTokenError)
async def nonexist_handler(request: Request,
                           exc: NonExistentTokenError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NotOperatorError)
async def notop_handler(request: Request,
                        exc: NotOperatorError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(NotClaimableError)
async def nonclaim_handler(request: Request,
                           exc: NotClaimableError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


@app.exception_handler(UnknownAccountError)
async def badacc_handler(request: Request,
                         exc: UnknownAccountError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.message}"},
    )


# API Methods
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


"""
@app.get("/users/items/view", tags=[tags[0]])
async def view_items(current_user: user_objects.User = Depends(
    get_current_user),
                     database: Session = Depends(get_db)) -> List:
"""
#View owned items of currently logged in user
"""
    owned_items = item_methods.get_user_items(database, TXReqs(),
                                              current_user.publickey.decode())
    if not owned_items:
        raise HTTPException(status_code=404, detail="No items found.")
    return owned_items
"""


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
        database, build_item_tx(database, current_user, passkey, item_id),
        item_id, receiver_attr)
    if not transferred_item:
        raise HTTPException(status_code=400, detail="Transfer failed.")
    return f"Item {item_id} transferred to user {receiver_attr}."


@app.get("/users/get", response_model=user_objects.UserDisplay, tags=[tags[0]])
def get_user(
    user_attr: str,
    database: Session = Depends(get_db),
    current_user: user_objects.User = Depends(get_current_user)
) -> user_objects.UserDisplay:
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
    database: Session = Depends(get_db),
    current_user: user_objects.User = Depends(get_current_user)
) -> str:
    """
    Create item token
    """
    created_item = item_methods.create_item(
        ipfs, build_mint_tx(current_user, passkey, database), item_obj_list)
    if not created_item:
        raise HTTPException(status_code=400, detail="Item creation failed.")
    return "Item created."


@app.post("/items/claim", tags=[tags[1]])
async def claim_item(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user),
    database: Session = Depends(get_db)
) -> str:
    """
    Claim Item Token
    """
    item_methods.claim_item(
        build_item_tx(database, current_user, passkey, item_id), item_id)
    return f"Item {item_id} has been claimed"


@app.post("/items/set/claimability", tags=[tags[1]])
async def toggle_item_claimability(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user),
    database: Session = Depends(get_db)
) -> str:
    """
    Toggle item claimability
    """
    item_methods.set_item_claimability(
        build_item_tx(database, current_user, passkey, item_id), item_id)
    return "Item claimability changed."


"""
@app.post("/items/set/missing", tags=[tags[1]])
async def toggle_item_missing(
        item_id: int,
        database: Session = Depends(get_db),
        current_user: user_objects.User = Depends(get_current_user)
) -> str:
"""
# Toggle item missing status
"""
    missing_status = item_methods.toggle_item_missing(database, TXReqs(), current_user, item_id)
    return f"{item_id} Missing Status: {missing_status}"
"""


@app.post("/items/forfeit", tags=[tags[1]])
async def forfeit_item(
    item_id: int,
    passkey: str,
    current_user: user_objects.User = Depends(get_current_user),
    database: Session = Depends(get_db)
) -> str:
    """
    Forfeit/burn Item Token
    """
    item_methods.burn_item_token(
        build_item_tx(database, current_user, passkey, item_id), item_id)
    return f"Item {item_id} forfeited."


@app.get("/items/get", response_model=item_objects.Item, tags=[tags[1]])
def get_item(
    item_id: int, database: Session = Depends(get_db)) -> item_objects.Item:
    """
    Display item token details by ID
    """
    item_obj = item_methods.get_item(build_item_call(database, item_id),
                                     item_id)
    if item_obj is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_obj


@app.get("/items/view/claimability", tags=[tags[1]])
async def view_item_claimability(
    item_id: int,
    current_user: user_objects.User = Depends(get_current_user),
    database: Session = Depends(get_db)
) -> str:
    """
    View item claimability
    """
    item_claimability = item_methods.get_item_claimability(
        build_item_call(database, item_id), item_id)
    return f"Item claimability status: {item_claimability}"


@app.get("/items/view/owner",
         response_model=user_objects.UserDisplay,
         tags=[tags[1]])
async def view_item_owner(
    item_id: int, database: Session = Depends(get_db)) -> str:
    """
    View owner of provided item token
    """
    tx_reqs = build_item_call(database, item_id)
    try:
        owner_publickey = tx_reqs.contract.functions.ownerOf(item_id).call()
    except:
        raise NonExistentTokenError
    owner_obj = database.query(db_schemas.User).filter(
        db_schemas.User.publickey == owner_publickey).options(
            load_only('id', 'publickey', 'username')).first()
    return owner_obj


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
