"""
Database connectivity
Using PostgreSQL
"""
from os import getenv

import ipfshttpclient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Connecting to database and creating a usage session
engine = create_engine(getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class declaration
Base = declarative_base()

# IPFS connection
ipfs = ipfshttpclient.connect(getenv('IPFS_URL'))
