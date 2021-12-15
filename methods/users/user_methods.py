# Cryptography modules
from ..crypto import aes_methods, sha_methods

# Utilities
from random import randrange

# Database tooling
from shortuuid import ShortUUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

# Local modules
from ..db import db_schemas
from . import user_objects

OPERATOR_ROLE = "0x97667070c54ef182b0f5858b034beac1b6f3089aa2d3188bb1e8929f4fa9b929"

### User Methods ###
# User creation
def create_user(db: Session, w3, user: user_objects.User):
    account = w3.eth.account.create()
    pubkey, privkey_raw = account.address, account.privateKey.hex()

    # Encrypting private key
    # USERS MUST STORE KEY WHERE IT WILL NOT BE LOST
    accesskey = aes_methods.aes_encrypt(privkey_raw, user.passkey)

    # Hashing user password
    passkey = sha_methods.create_hash(user.passkey)

    # Committing to database
    db_user = db_schemas.User(
        id=ShortUUID().random(length=10),
        username=user.username,
        email=user.email,
        publickey=pubkey,
        accesskey=accesskey,
        passkey=passkey,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Returning user object
    return db_user

# Verifying user by password
def verify_user(db: Session, user_attr: str, passkey: str):
    db_user = get_user_by(db, user_attr)
    if not db_user:
        return False
    if not sha_methods.verify_hash(passkey, db_user.passkey):
        return False
    
    # Returning user object
    return db_user

# Gets user by either username, publickey, email or ID
def get_user_by(db: Session, user_attr: str):
    db_user = (
        db.query(db_schemas.User)
        .filter(
            or_(
                db_schemas.User.username == user_attr,
                db_schemas.User.publickey == user_attr,
                db_schemas.User.email == user_attr,
                db_schemas.User.id == user_attr,
            )
        )
        .first()
    )
    
    # Returning user object
    return db_user

# Get all users
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_schemas.User).offset(skip).limit(limit).all()

### Operator Methods ###
# Setting user as operator
def set_operator(db: Session, contract, user_attr: str, brand: str):
    db_user = get_user_by(db, user_attr)
    contract.functions.grantRole(OPERATOR_ROLE, db_user.publickey).transact({"from":"0x5388004a20e069709045DDEAC684586986472747"})
    db.query(db_schemas.User).filter(db_schemas.User.id == db_user.id).update(
        {"type": "operator", "brand": brand}
    )
    db.commit()
    db.refresh(db_user)

    # Returning user object
    return db_user

# Verifies that user is operator. Returns true/false
def is_operator(contract, user: user_objects):
    status = contract.functions.hasRole(OPERATOR_ROLE, user.publickey)
    if user.type == db_schemas.AccountType.operator and status:
        return True
    else:
        return False
