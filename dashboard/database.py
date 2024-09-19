"""Define an instance logger that logs to the WorkflowInstanceEvent table."""

from typing import Optional

from flask import current_app, g

from autodoc.db import Database, DatabaseManager
from autodoc.workflow import EventLoggerInterface


def get_manager():
    """Load database manager from application context."""
    if not hasattr(g, "manager"):
        DB_PATH = current_app.config["DB_PATH"]
        g.manager = DatabaseManager(db=Database(db_file=DB_PATH))

    return g.manager


def close_db(e=None):
    """Close the database connection at the end of the application context."""
    manager = g.pop("manager", None)

    if manager:
        manager.db.close()


def init_app(app):
    """Add teardown to the app."""
    app.teardown_appcontext(close_db)


class InstanceLog(EventLoggerInterface):
    """Provide database actions for logging instances."""

    def __init__(self) -> None:
        """Initialise the instance logger."""
        # self.cm = cm

    def write_source_event(
        self,
        instance_id: int,
        source_id: Optional[int],
        source_data: dict,
        source_data_ongoing: dict,
    ) -> None:
        """Write a source event to the instance table."""

    def write_outcome_event(self, instance_id: int, outcome_id: int, outcome_location: str) -> None:
        """Write an outcome event to the event log table."""


instance_log = InstanceLog()
