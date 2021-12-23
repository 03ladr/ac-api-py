"""
FastAPI-required objects
"""
# Typing
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str

tags = ("User Methods", "Item Methods", "Utility Endpoints")  # FastAPI visual tags
