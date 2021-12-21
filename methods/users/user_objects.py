# Typing
from typing import Optional
from pydantic import BaseModel, constr
from ..database.db_schemas import AccountType

# User Objects
UserID = constr(min_length=10, max_length=10)


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    passkey: str


class User(BaseModel):
    id: UserID
    username: str
    email: str
    publickey: bytes

    class Config:
        orm_mode = True


class Operator(User):
    brand: Optional[str] = None

    class Config:
        orm_mode = True


class Account(Operator):
    type: AccountType
