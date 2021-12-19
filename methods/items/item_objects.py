# Typing
from typing import Optional, List
from pydantic import BaseModel

class ItemAttribute(BaseModel):
    trait_type: Optional[str] = None
    value: Optional[str] = None

class ItemCreate(BaseModel):
    name: str
    description: str
    image: str
    date: str
    brand: str
    lister: str
    attributes: List[ItemAttribute]

class Item(ItemCreate):
    id: int

    class Config:
        orm_mode = True
