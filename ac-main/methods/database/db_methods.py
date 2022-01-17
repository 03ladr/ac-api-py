"""
Database methods
"""
# Database Connectivity/Tooling
from .utils.db_filter import ItemFilters
from .database import Base, SessionLocal, engine
from sqlalchemy.orm import Session
# On-Chain Connectivity/Tooling
from ..onchain.onchain_config import contract
# Utilities
from asyncio import sleep


def load_db() -> bool:
    """
    Creates database tables
    """
    Base.metadata.create_all(bind=engine)
    return True


async def populate_db() -> None:
    """
    Smart contract event log filter -> database population
    """
    itemfilter = ItemFilters(SessionLocal(), contract)
    while True:
        itemfilter.filter()
        await sleep(5)


def get_db() -> Session:
    """
    Database context manager
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
