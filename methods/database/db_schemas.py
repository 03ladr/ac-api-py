"""
Database schemas
"""
# Utilities
import enum
# Database Connectivity/Tooling
from sqlalchemy import Enum, Column, Integer, String, Boolean, DateTime, Interval
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
    brand = Column(String, unique=True, nullable=True)


class Item(Base):
    """
    Item Database Table
    """
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    transfers = Column(Integer)
    holdtime_avg = Column(Interval)
    creation_date = Column(DateTime)
    missing_status = Column(Boolean, default=False)
    report_to = Column(String, nullable=True)
