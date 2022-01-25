"""
User Methods/Functions
"""
from shortuuid import ShortUUID
from sqlalchemy import or_
from sqlalchemy.orm import Session, load_only

from ..cryptography import aes_methods, sha_methods
from ..database import db_schemas
from ..exceptions.exception_objects import UnknownAccountError
from . import user_objects


def create_user(database: Session, w3,
                user: user_objects.User) -> db_schemas.User:
    """
    Create User Account
    """
    account = w3.eth.account.create()
    pubkey, privkey_raw = bytes(account.address,
                                'utf-8'), account.privateKey.hex()
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
    database.add(db_user)
    database.commit()
    database.refresh(db_user)
    # Returning user object
    return db_user


def verify_user(database: Session, user_attr: str,
                passkey: str) -> db_schemas.User:
    """
    Verify user by password
    """
    db_user = get_user_by(database, user_attr)
    if not db_user:
        return False
    if not sha_methods.verify_hash(passkey, db_user.passkey):
        return False
    # Returning user object
    return db_user


def get_user_by(database: Session, user_attr: str) -> db_schemas.User:
    """
    Get user by:
        - username
        - public key
        - emails
        - ID
    """
    db_user = (database.query(db_schemas.User).filter(
        or_(
            db_schemas.User.username == user_attr,
            db_schemas.User.publickey == bytes(user_attr, 'utf-8'),
            db_schemas.User.email == user_attr,
            db_schemas.User.id == user_attr,
        )).first())
    # Returning user object
    return db_user


def get_user_publickey(database: Session, user_attr: str) -> bytes:
    """
    Get public key of user
    """
    publickey = (database.query(db_schemas.User).filter(
        or_(db_schemas.User.username == user_attr,
            db_schemas.User.email == user_attr,
            db_schemas.User.id == user_attr)).options(
                load_only('publickey')).first())
    if not publickey:
        raise UnknownAccountError
    # Returns users public key
    return publickey.publickey


def get_users(database: Session,
              skip: int = 0,
              limit: int = 100) -> db_schemas.User:
    """
    Get all users
    """
    return database.query(db_schemas.User).offset(skip).limit(limit).all()
