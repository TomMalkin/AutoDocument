"""Define outcome views."""

from werkzeug.wrappers.response import Response
from flask import Blueprint, redirect, url_for
from dashboard.database import get_db_manager

from typing import Union

bp = Blueprint("outcome", __name__)


@bp.route("/delete_outcome/<workflow_id>/<outcome_id>", methods=["GET", "POST"])
def delete_outcome_view(workflow_id: int, outcome_id: int) -> Union[str, Response]:
    """Delete a outcome."""
    manager = get_db_manager()
    manager.outcomes.delete(outcome_id=outcome_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
