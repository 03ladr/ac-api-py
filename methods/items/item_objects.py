# Typing
from typing import Optional
from pydantic import BaseModel


# Item Objects
# There must be a way to better 'map' the item attributes - i.e. nested
# within ItemCreate.


class ItemAttribute(BaseModel):
    trait_type: Optional[str] = None
    value: Optional[str] = None


class ItemAttributes(BaseModel):
    a1: ItemAttribute
    a2: ItemAttribute
    a3: ItemAttribute


class ItemCreate(BaseModel):
    name: str
    description: str
    image: str
    date: str
    brand: str
    lister: str
    attributes: ItemAttributes


class Item(BaseModel):
    id: int

    class Config:
        orm_mode = True
