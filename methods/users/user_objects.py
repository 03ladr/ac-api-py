"""
User Objects
"""
# Typing
from typing import Optional
from pydantic import BaseModel, constr
from ..database.db_schemas import AccountType

# User ID Object
UserID = constr(min_length=10, max_length=10)

# Base User Object
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    passkey: str

# User Object
class User(BaseModel):
    id: UserID
    username: str
    email: str
    publickey: bytes

    class Config:
        orm_mode = True

# Operator Object
class Operator(User):
    brand: Optional[str] = None

    class Config:
        orm_mode = True

# Account Type Enum Object
class Account(Operator):
    type: AccountType

    class Config:
        orm_mode = True
