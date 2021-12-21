"""
FastAPI-required objects
"""
# Typing
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str

tags = ("User Methods", "Operator Methods", "Lookup Methods",
        "Utility Endpoints", "Item Verification")  # FastAPI visual tags
