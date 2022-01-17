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
engine = create_engine("postgresql://plasma:pass@localhost/authentichain")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class declaration
Base = declarative_base()

# IPFS connection
ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")
