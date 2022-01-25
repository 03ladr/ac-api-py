"""
User Objects
"""
from typing import Optional

from pydantic import BaseModel, constr

from ..database.db_schemas import AccountType


UserID = constr(min_length=10, max_length=10)


class UserBase(BaseModel):
    """
    Base User Object
    """
    username: Optional[str] = None
    email: Optional[str] = None
    passkey: str


class UserDisplay(BaseModel):
    """
    User 'Display' Object
    No sensitive information is included
    """
    id: UserID
    username: str
    publickey: bytes

    class Config:
        orm_mode = True


class User(UserDisplay):
    """
    User Object
    """
    email: str

    #class Config:
    #    orm_mode = True


class Account(User):
    """
    Account Type Enum Object
    """
    type: AccountType

    #class Config:
    #    orm_mode = True
