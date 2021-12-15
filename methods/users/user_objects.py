# Typing
from typing import List, Optional
from pydantic import BaseModel, constr
from ..items.item_objects import Item
from ..db.db_schemas import AccountType


# User Objects
UserID = constr(min_length=10, max_length=10)

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    passkey: str


class UserDisplay(BaseModel):
    id: UserID
    type: AccountType
    username: str
    email: str
    publickey: str

    class Config:
        orm_mode = True


class User(UserDisplay):
    accesskey: str
    brand: Optional[str] = None
    items: List[Item] = []

    class Config:
        orm_mode = True
