"""
Database methods
"""
from asyncio import sleep

from sqlalchemy.orm import Session

from ..onchain.onchain_config import proxy_contract
from .database import Base, SessionLocal, engine
from .db_filter import TokenFilters


def load_db() -> bool:
    """
    Creates database tables
    """
    Base.metadata.create_all(bind=engine)
    return True


async def populate_db() -> None:
    """
    Proxy smart contract event log filter -> database population
    """
    itemfilter = TokenFilters(SessionLocal(), proxy_contract)
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
