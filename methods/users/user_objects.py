"""
User Objects
"""
# Typing
from typing import Optional
from pydantic import BaseModel, constr
from ..database.db_schemas import AccountType
# User ID Object


UserID = constr(min_length=10, max_length=10)


class UserBase(BaseModel):
    """
    Base User Object
    """
    username: Optional[str] = None
    email: Optional[str] = None
    passkey: str


class User(BaseModel):
    """
    User Object
    """
    id: UserID
    username: str
    email: str
    publickey: bytes

    class Config:
        orm_mode = True


class Operator(User):
    """
    Operator Object
    """
    brand: Optional[str] = None

    class Config:
        orm_mode = True


class Account(Operator):
    """
    Account Type Enum Object
    """
    type: AccountType
    reporting: bool

    class Config:
        orm_mode = True
