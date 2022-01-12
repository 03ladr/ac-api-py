"""
Database schemas
"""
# Utilities
import enum
# Database Connectivity/Tooling
from sqlalchemy import Enum, Column, Integer, String, Boolean, DateTime, Interval, INET
from sqlalchemy.types import LargeBinary
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
    from = Column(LargeBinary, index=True)
    from_ip = Column(INET, index=True)
