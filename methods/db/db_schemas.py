"""
Database schemas
"""
# Database Connectivity/Tooling
from sqlalchemy import Enum, Column, Integer, String
from sqlalchemy.types import LargeBinary
from .database import Base
# Utilities
import enum


# Account types
class AccountType(enum.Enum):
    user = "user"
    operator = "operator"


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    publickey = Column(LargeBinary, unique=True, index=True)
    accesskey = Column(LargeBinary, unique=True)
    passkey = Column(LargeBinary)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    type = Column(Enum(AccountType), server_default="user")
    brand = Column(String, unique=True, nullable=True)


# Item Table
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    transfers = Column(Integer)
