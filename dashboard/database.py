"""Define an instance logger that logs to the WorkflowInstanceEvent table."""

from flask import Flask, current_app, g

from autodoc.data import DatabaseManager


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
