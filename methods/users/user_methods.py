"""
User Methods/Functions
"""
# Cryptography modules
from ..cryptography import aes_methods, sha_methods
# Utilities
from config import CONTRACT_CREATOR
# Database Connectivity/Tooling
from shortuuid import ShortUUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import db_schemas
# User Modules
from . import user_objects


OPERATOR_ROLE = "0x97667070c54ef182b0f5858b034beac1b6f3089aa2d3188bb1e8929f4fa9b929"


def create_user(db: Session, w3, user: user_objects.User) -> user_objects.User:
    """
    Create User Account
    """
    account = w3.eth.account.create()
    pubkey, privkey_raw = bytes(account.address,
                                'utf-8'), account.privateKey.hex()
    # Encrypting private key
    # USERS MUST STORE KEY WHERE IT WILL NOT BE LOST
    accesskey = aes_methods.aes_encrypt(privkey_raw)
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


def verify_user(db: Session, user_attr: str, passkey: str) -> user_objects.User:
    """
    Verify user by password
    """
    db_user = get_user_by(db, user_attr)
    if not db_user:
        return False
    if not sha_methods.verify_hash(passkey, db_user.passkey):
        return False
    # Returning user object
    return db_user


def get_user_by(db: Session, user_attr: str) -> user_objects.User:
    """
    Get user by:
        - username
        - public key
        - emails
        - ID
    """
    db_user = (db.query(db_schemas.User).filter(
        or_(
            db_schemas.User.username == user_attr,
            db_schemas.User.publickey == bytes(user_attr, 'utf-8'),
            db_schemas.User.email == user_attr,
            db_schemas.User.id == user_attr,
        )).one())
    # Returning user object
    return db_user


def get_user_publickey(db: Session, user_attr: str) -> bytes:
    """
    Get public key of user
    """
    publickey = (db.query(db_schemas.User).filter(
        or_(
            db_schemas.User.username == user_attr,
            db_schemas.User.publickey == bytes(user_attr, 'utf-8'),
            db_schemas.User.email == user_attr,
            db_schemas.User.id == user_attr,
        )).options(load_only('publickey')).one())
    return publickey


def get_users(db: Session, skip: int = 0, limit: int = 100) -> user_objects.User:
    """
    Get all users
    """
    return db.query(db_schemas.User).offset(skip).limit(limit).all()


"""OPERATOR METHODS"""
def set_operator(db: Session, contract, user_attr: str, brand: str) -> user_objects.User:
    """
    Set user as operator
    """
    db_user = get_user_by(db, user_attr)
    contract.functions.grantRole(OPERATOR_ROLE,
                                 db_user.publickey.decode()).transact(
                                     {"from": CONTRACT_CREATOR})
    db.query(db_schemas.User).filter(db_schemas.User.id == db_user.id).update({
        "type": "operator", "brand": brand}
    )
    db.commit()
    db.refresh(db_user)
    # Returning user object
    return db_user


def is_operator(contract, user: user_objects.User) -> bool:
    """
    Verify that user is an operator. Returns True/False
    """
    status = contract.functions.hasRole(OPERATOR_ROLE, user.publickey.decode())
    if user.type == db_schemas.AccountType.operator and status:
        return True
    else:
        return False
