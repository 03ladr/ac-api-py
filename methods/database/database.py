"""
Database connectivity
Using PostgreSQL
"""
# Config Variables
from os import getenv
# Database Connectivity/Tooling
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ipfshttpclient

# Connecting to database and creating a usage session
engine = create_engine(getenv(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class declaration
Base = declarative_base()

# IPFS connection
ipfs = ipfshttpclient.connect(getenv(IPFS_URL))
