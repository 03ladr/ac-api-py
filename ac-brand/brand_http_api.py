"""
Authentichain Brand HTTP API
FastAPI-Based
"""
# import fastapi
from sqlalchemy.orm import Session

from methods.database.db_methods import get_db, load_db, populate_db

# Initialization
"""DB INIT"""
load_db()
""" WEB3 FILTER -> DATABASE POPULATION """
create_task(populate_db())
