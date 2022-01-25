"""
Item Objects
"""
from typing import List, Optional

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
    brand: str
    attributes: List[ItemAttribute]


class Item(ItemCreate):
    """
    Item Database Object
    """
    id: int
    transfers: int
    verifications = int
    stolen_status = bool
    lost_status = bool

    class Config:
        orm_mode = True
