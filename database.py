"""
Database Configuration Module
Handles SQLite connection engine, session management, and Base declarative model.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Local SQLite database file path
SQLALCHEMY_DATABASE_URL = "sqlite:///./students.db"

# connect_args={"check_same_thread": False} is required for SQLite to support multi-threading in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures the session is automatically closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
