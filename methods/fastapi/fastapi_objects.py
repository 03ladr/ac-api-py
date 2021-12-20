# Typing
from pydantic import BaseModel

### JWT Objects ###
class Token(BaseModel):
    access_token: str
class TokenData(BaseModel):
    id: str
    type: str

### FastAPI Objects ###
tags = (
    "User Methods",
    "Operator Methods",
    "Lookup Methods",
    "Utility Endpoints",
    "Item Verification"
)  # FastAPI visual tags
