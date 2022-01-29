"""
Database schemas
"""
from sqlalchemy import Column, DateTime, Integer, Interval
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


class TransferLog(Base):
    """
    Transfer Log Table
    """
    __tablename__ = "transferlog"
    tx_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, index=True)
    date = Column(DateTime)
    sent_to = Column(LargeBinary, index=True)
    sent_from = Column(LargeBinary, index=True)
