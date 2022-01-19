"""
Authentichain Brand HTTP API
FastAPI-Based
"""
# FastAPI Dependencies/Tooling
#import fastapi
# Dependency Connectivity/Tooling
from sqlalchemy.orm import Session
from methods.database.db_methods import load_db, populate_db, get_db

"""DB INIT"""
load_db()
""" WEB3 FILTER -> DATABASE POPULATION """
create_task(populate_db())

