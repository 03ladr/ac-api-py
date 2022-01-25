"""
FastAPI-required objects
"""
from pydantic import BaseModel


class Token(BaseModel):
    """
    JWT Token
    """
    access_token: str


tags = ("User Methods", "Item Methods", "Utility Endpoints"
        )  # FastAPI visual tags
