"""Define outcome views."""

from ...models import delete_outcome
from werkzeug.wrappers.response import Response
from flask import Blueprint, redirect, url_for

from typing import Union

bp = Blueprint("outcome", __name__)


@bp.route("/delete_outcome/<workflow_id>/<outcome_id>", methods=["GET", "POST"])
def delete_outcome_view(workflow_id: int, outcome_id: int) -> Union[str, Response]:
    """Delete a outcome."""
    delete_outcome(outcome_id=outcome_id)
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
