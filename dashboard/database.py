"""Define an instance logger that logs to the WorkflowInstanceEvent table."""

from typing import Optional

from flask import current_app, g, Flask

# from autodoc.db import Database, DatabaseManager
from autodoc.workflow import EventLoggerInterface
# from autodoc.orm import create_session
from autodoc.data import DatabaseManager



# def get_manager():
#     """Load database manager from application context."""
#     if not hasattr(g, "manager"):
#         DB_PATH = current_app.config["DB_PATH"]
#         g.manager = DatabaseManager(db=Database(db_file=DB_PATH))
#
#     return g.manager
#
#
# def get_orm_manager():
#     """Load database manager from application context."""
#     if not hasattr(g, "orm_manager"):
#         DB_PATH = current_app.config["DB_PATH"]
#         g.orm_manager = create_session(db_file=DB_PATH)
#
#     return g.orm_manager
#
#
# def get_session():
#     """Load a database object to use for ORM models."""
#     if not hasattr(g, "session"):
#         DB_PATH = current_app.config["DB_PATH"]
#         print(DB_PATH)
#         # engine = create_engine(os.path.join("sqlite://", DB_PATH))
#         # engine = create_engine("sqlite:///database/autodoc.db")
#         engine = create_engine("sqlite:///" + DB_PATH)
#         g.session = Session(engine)
#
#     return g.session


def get_db_manager() -> DatabaseManager:
    """Load and return the database manager from Flask's application context."""
    if "db_manager" not in g:
        DB_PATH = current_app.config.get("DB_PATH", "./database/autodoc.db")
        g.db_manager = DatabaseManager(db_file=DB_PATH)
    return g.db_manager


def register_db_teardown(app: Flask):
    """Register a teardown function to ensure the database session is closed."""

    @app.teardown_appcontext
    def close_db_session(exception):
        """Ensure the database session is closed at the end of the request."""
        db_manager = g.pop("db_manager", None)
        if db_manager:
            db_manager.close()


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
