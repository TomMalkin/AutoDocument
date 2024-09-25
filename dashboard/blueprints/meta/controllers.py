"""Define views for meta based controllers."""

from typing import Union
from werkzeug.wrappers.response import Response
from .forms import (
    CreateMetaDatabase,
    CreateMetaFileSystem,
    CreateMetaS3,
    CreateMetaWindowsFileSystem,
    CreateMetaSharePoint,
)
from flask import Blueprint, redirect, render_template, request, url_for
from dashboard.database import get_manager
from flask_login import login_required
from loguru import logger

meta_blueprint = Blueprint("meta", "meta_blueprint")


@meta_blueprint.route("/")
@login_required
def index() -> Union[str, Response]:
    """Render the advanced page with database and filesystem management."""
    manager = get_manager()
    databases = manager.get_meta_databases().data
    database_form = CreateMetaDatabase()

    posix_filesystems = manager.get_posix_filesystems().data
    posix_filesystem_form = CreateMetaFileSystem()

    windows_filesystems = manager.get_windows_filesystems().data
    windows_filesystem_form = CreateMetaFileSystem()

    s3s = manager.get_s3_filesystems().data
    s3_form = CreateMetaS3()

    sharepoints = manager.get_sharepoints().data
    sharepoint_form = CreateMetaSharePoint()

    database_options = [
        ("mysql", "MySQL/MariaDB"),
        ("postgresql", "PostgreSQL"),
        ("sqlite", "SQLite"),
        ("mssql", "Microsoft SQL Server"),
    ]

    return render_template(
        "meta/index.html",
        databases=databases,
        database_form=database_form,
        posix_filesystems=posix_filesystems,
        posix_form=posix_filesystem_form,
        windows_filesystems=windows_filesystems,
        windows_form=windows_filesystem_form,
        s3s=s3s,
        s3_form=s3_form,
        sharepoints=sharepoints,
        sharepoint_form=sharepoint_form,
        database_options=database_options,
    )



@meta_blueprint.route("/add_meta_database", methods=["POST"])
def add_meta_database() -> Union[str, Response]:
    """Add a metadatabase."""
    manager = get_manager()
    form = CreateMetaDatabase()

    mapping = {
        "mysql": "mysql+mysqlconnector",
        "postgresql": "postgresql+psycopg2",
        "sqlite": "sqlite",
        "mssql": "mssql+pyodbc",
    }

    if form.validate_on_submit():
        name = form.name.data
        database = form.database.data
        connection_string = form.connection_string.data
        full_connection_string = f"{mapping[database]}://{connection_string}"
        logger.info(f"Given {database=} and {connection_string=}, {full_connection_string=}")
        manager.add_meta_database(name=name, connection_string=full_connection_string)

    return redirect(url_for("meta.index"))


@meta_blueprint.route("/add_posix_fs", methods=["POST"])
def add_posix_fs() -> Union[str, Response]:
    """Add a posix filesystem."""
    manager = get_manager()
    form = CreateMetaFileSystem()

    if form.validate_on_submit():
        local_path = form.local_path.data.rstrip("/") + "/"
        remote_path = form.remote_path.data.rstrip("/") + "/"

        manager.add_posix_filesystem(local_path=local_path, remote_path=remote_path)

    return redirect(url_for("meta.index"))


@meta_blueprint.route("/add_windows_fs", methods=["POST"])
def add_windows_fs() -> Union[str, Response]:
    """Add a windows filesystem."""
    manager = get_manager()
    form = CreateMetaWindowsFileSystem()

    if form.validate_on_submit():
        local_path = form.local_path.data.rstrip("/") + "/"
        remote_path = form.remote_path.data.rstrip("\\") + "\\"
        manager.add_windows_filesystem(local_path=local_path, remote_path=remote_path)

    return redirect(url_for("meta.index"))


@meta_blueprint.route("/add_s3", methods=["POST"])
def add_s3() -> Union[str, Response]:
    """Add a windows filesystem."""
    manager = get_manager()
    form = CreateMetaS3()

    if form.validate_on_submit():
        url = form.url.data
        username = form.username.data
        password = form.password.data
        manager.add_s3(url=url, username=username, password=password)

    return redirect(url_for("meta.index"))

@meta_blueprint.route("/add_sharepoint", methods=["POST"])
def add_sharepoint() -> Union[str, Response]:
    """Add a windows filesystem."""
    manager = get_manager()
    form = CreateMetaSharePoint()

    if form.validate_on_submit():
        url = form.url.data
        username = form.username.data
        password = form.microsoft_password.data
        library = form.library.data
        manager.add_sharepoint(url=url, username=username, password=password, library=library)

    return redirect(url_for("meta.index"))

@meta_blueprint.route("/component/connection_string")
def connection_string_component():
    """Return an input box with a placeholder for the type of database."""
    database = request.args.get("database")
    logger.debug(f"Getting file accessor form snippet for {database=}")

    mapping = {
        "mysql": "<username>:<password>@<host>:<port>/<database>",
        "postgresql": "<username>:<password>@<host>:<port>/<database>",
        "sqlite": "<file path>",
        "mssql": "<username>:<password>@<host>:<port>/<database>?driver=ODBC+Driver+17+for+SQL+Server",
    }
    placeholder = mapping.get(database, "")

    return render_template("meta/connection_string.html", placeholder=placeholder)


