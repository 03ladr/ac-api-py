"""
Database schemas
"""
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Interval,
    String,
)
from sqlalchemy.types import LargeBinary
from sqlalchemy.dialects.postgresql import INET

from .database import Base


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


class TransferLog(Base):
    """
    Transfer Log Table
    """
    __tablename__ = "transferlog"
    tx_id = Column(Integer, primary_key=True)
    id = Column(Integer, index=True)
    date = Column(DateTime)
    to = Column(LargeBinary, index=True)
    sent_from = Column(LargeBinary, index=True)
    from_ip = Column(INET, index=True)
