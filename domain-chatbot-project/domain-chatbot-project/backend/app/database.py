# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# Engine is the core interface to the database
engine = create_engine(
    settings.database_url,
    # Connection pool settings for better performance
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create SessionLocal class
# SessionLocal will be used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for our models
# All database models will inherit from this Base class
Base = declarative_base()

# Dependency function to get database session
def get_db():
    """
    This function creates a database session and ensures it gets closed
    after the request is completed. FastAPI will inject this dependency
    into our route functions.
    """
    db = SessionLocal()
    try:
        yield db  # This provides the session to the route function
    finally:
        db.close()  # Always close the session when done

# Why this structure?
# 1. Engine: Manages database connections and connection pool
# 2. SessionLocal: Factory for creating database sessions
# 3. Base: Common base class for all our database models
# 4. get_db(): Dependency injection pattern for database sessions