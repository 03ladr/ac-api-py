"""
Database methods
"""
# Database Connectivity/Tooling
from .utils.db_filter import ItemFilters
from .database import Base, SessionLocal, engine
# On-Chain Connectivity/Tooling
from ..onchain.onchain_config import contract
# Utilities
from asyncio import sleep


def load_db():
    Base.metadata.create_all(bind=engine)  # Create DB tables
    return True


async def populate_db():  # Contract event log -> database population
    itemfilter = ItemFilters(SessionLocal(), contract)
    while True:
        itemfilter.filter()
        await sleep(5)


def get_db():  # DB context manager
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
