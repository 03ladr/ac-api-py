# Database connectivity/tooling
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connecting to database and creating a usage session
DATABASE_URL = "postgresql://plasma:pass@localhost/authentichain"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class declaration
Base = declarative_base()
