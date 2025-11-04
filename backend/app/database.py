"""Database configuration and SQLAlchemy engine setup."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database URL from environment variable with default for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cleantwin"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries for debugging
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max overflow connections
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
