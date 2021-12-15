import enum
from sqlalchemy import Numeric, Enum, Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.types import LargeBinary
from .db import Base

# Account types
class AccountType(enum.Enum):
    user = "user"
    operator = "operator"


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    publickey = Column(String, unique=True, index=True)
    accesskey = Column(String, unique=True)
    passkey = Column(String)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    type = Column(Enum(AccountType), server_default="user")
    brand = Column(String, unique=True, nullable=True)


# Item Table
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
