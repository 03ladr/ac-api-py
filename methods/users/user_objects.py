# Typing
from typing import List, Optional
from pydantic import BaseModel
from ..items.item_objects import ItemDisplay
from ..db.db_schemas import AccountType
from ..vars.strids import UserID


# User Objects
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
    items: List[ItemDisplay] = []

    class Config:
        orm_mode = True
