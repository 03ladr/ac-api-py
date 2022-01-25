from datetime import datetime, timedelta
from os import getenv
from typing import Optional

from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..database import db_schemas
from ..database.db_methods import get_db
from ..exceptions.exception_objects import CredentialError
from ..fastapi.fastapi_config import oauth2_scheme

JWTKEY = getenv('JWTKEY')


# API Functions
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


def jwt_decoder(token: str) -> str:
    """
    Decode JWT
    """
    try:
        jwt_decoded = jwt.decode(token, JWTKEY, algorithms=["HS256"])
        user_id = jwt_decoded.get("id")
        if user_id is None:
            raise CredentialError
    except JWTError:
        raise CredentialError
    return user_id


def get_current_user(database: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)) -> db_schemas.User:
    """
    Obtains details of currently logged in user
    """
    user_id = jwt_decoder(token)
    db_user = database.query(
        db_schemas.User).filter(db_schemas.User.id == user_id).first()
    if db_user is None:
        raise CredentialError
    return db_user
