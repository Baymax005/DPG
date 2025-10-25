"""
Database Configuration
Handles PostgreSQL connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - can be local or Railway
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# For SQLite (simpler for local development)
# Uncomment this if you don't have PostgreSQL yet
# DATABASE_URL = "sqlite:///./dpg.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    # For SQLite, use:
    # connect_args={"check_same_thread": False}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency function to get database session
    Ensures session is closed after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
