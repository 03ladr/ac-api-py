"""
Database schemas
"""
import enum

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.types import LargeBinary

from .database import Base


class AccountType(enum.Enum):
    """
    Account Type Enum Object
    """
    user = "user"
    operator = "operator"


class User(Base):
    """
    User Database  Table
    """
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    publickey = Column(LargeBinary, unique=True, index=True)
    accesskey = Column(LargeBinary, unique=True)
    passkey = Column(LargeBinary)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    type = Column(Enum(AccountType), server_default="user")


class Operator(Base):
    """
    Opereator Database Table
    """
    __tablename__ = "operators"
    id = Column(String, primary_key=True, index=True)
    contract = Column(LargeBinary, unique=True, index=True)


class Item(Base):
    """
    Item Database Table
    """
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    contract = Column(LargeBinary, index=True)
