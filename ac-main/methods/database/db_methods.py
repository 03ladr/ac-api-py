"""
Database methods
"""
from asyncio import sleep

from sqlalchemy.orm import Session

from ..onchain.onchain_config import mint_contract
from .database import Base, SessionLocal, engine
from .utils.db_filter import ItemFilters


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
    itemfilter = ItemFilters(SessionLocal(), mint_contract)
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
