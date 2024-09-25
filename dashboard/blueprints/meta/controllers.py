"""Define views for meta based controllers."""

from typing import Union
from werkzeug.wrappers.response import Response
from flask import Blueprint, render_template, request
from flask_login import login_required
from loguru import logger

meta_blueprint = Blueprint("meta", "meta_blueprint")


@meta_blueprint.route("/")
@login_required
def index() -> Union[str, Response]:
    """Render the advanced page with database and filesystem management."""
    return render_template(
        "meta/index.html",
    )


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
