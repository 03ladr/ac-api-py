"""
Item Objects
"""
# Typing
from typing import Optional, List
from pydantic import BaseModel


class ItemAttribute(BaseModel):
    """
    Item Attribute Object
    """
    trait_type: Optional[str] = None
    value: Optional[str] = None


class ItemCreate(BaseModel):
    """
    Item Creation Object
    """
    name: str
    description: str
    image: str
    date: str
    brand: str
    lister: str
    attributes: List[ItemAttribute]


class Item(ItemCreate):
    """
    Item Database Object
    """
    id: int
    transfers: int

    class Config:
        orm_mode = True
