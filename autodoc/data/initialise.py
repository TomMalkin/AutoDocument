"""A safe database initialiser that can be safely run even if database already exists."""

from .tables import Base
from .manager import DatabaseManager
from loguru import logger


def initialise_database(db_file: str):
    """Create the schema for a new database and seed type tables."""
    manager = DatabaseManager(db_file=db_file)
    logger.info("Creating all")
    Base.metadata.create_all(manager.engine)

    logger.info("seeding type tables")

    manager.source_types.seed()
    manager.outcome_types.seed()
    manager.storage_types.seed()

    manager.commit()
