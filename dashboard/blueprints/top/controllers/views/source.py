"""Define source views."""

from typing import Union

from flask import Blueprint, redirect, url_for
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

bp = Blueprint("source", __name__)


@bp.route("/delete_source/<workflow_id>/<source_id>", methods=["GET", "POST"])
def delete_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
    """Delete a source."""
    manager = get_db_manager()
    manager.sources.delete(source_id=source_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
