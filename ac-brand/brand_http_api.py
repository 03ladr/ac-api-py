"""
Authentichain Brand HTTP API
FastAPI-Based
"""
# FastAPI Dependencies/Tooling
#import fastapi
# Dependency Connectivity/Tooling
from sqlalchemy.orm import Session

from methods.database.db_methods import get_db, load_db, populate_db


# Initialization
"""DB INIT"""
load_db()
""" WEB3 FILTER -> DATABASE POPULATION """
create_task(populate_db())
