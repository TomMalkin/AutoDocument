"""Provide utilities for creating SQLAlchemy sessions for SQLite databases."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session(db_file: str):
    """Create a SQLAlchemy session factory for a given SQLite database file."""
    engine = create_engine(f"sqlite:///{db_file}", echo=True, future=True)
    return sessionmaker(bind=engine, autoflush=False)
