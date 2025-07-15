"""Define the Meta Database blueprint."""

from typing import cast

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

from dashboard.database import get_db_manager

from .forms import CreateMetaDatabase

bp = Blueprint("db", "db")


@bp.route("/manage", methods=["GET"])
@login_required
def manage():
    """Manage database connections."""
    manager = get_db_manager()
    databases = manager.database_meta_sources.get_all()

    database_form = CreateMetaDatabase()

    database_options = [
        ("mysql", "MySQL/MariaDB"),
        ("postgresql", "PostgreSQL"),
        ("sqlite", "SQLite"),
        ("mssql", "Microsoft SQL Server"),
    ]
    return render_template(
        "meta/database.html",
        databases=databases,
        database_form=database_form,
        database_options=database_options,
    )


@bp.route("/delete_database/<database_id>")
@login_required
def delete(database_id):
    """Delete a database based on the id."""
    manager = get_db_manager()
    manager.database_meta_sources.delete(database_id=database_id)
    return redirect(url_for("meta.db.manage"))


@bp.route("/add_database", methods=["POST"])
@login_required
def add():
    """Add a database based on form input."""
    manager = get_db_manager()

    form = CreateMetaDatabase()

    mapping = {
        "mysql": "mysql+mysqlconnector",
        "postgresql": "postgresql+psycopg2",
        "sqlite": "sqlite",
        "mssql": "mssql+pyodbc",
    }

    if form.validate_on_submit():
        name = cast(str, form.name.data)
        database = form.database.data
        connection_string = form.connection_string.data
        full_connection_string = f"{mapping[database]}://{connection_string}"
        manager.database_meta_sources.add(name=name, connection_string=full_connection_string)

    return redirect(url_for("meta.db.manage"))
