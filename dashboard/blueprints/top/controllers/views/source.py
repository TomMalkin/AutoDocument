"""Define source views."""

from werkzeug.wrappers.response import Response
from flask import Blueprint, redirect, url_for
from dashboard.database import get_db_manager

from typing import Union

bp = Blueprint("source", __name__)


@bp.route("/delete_source/<workflow_id>/<source_id>", methods=["GET", "POST"])
def delete_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
    """Delete a source."""
    manager = get_db_manager()
    manager.sources.delete(source_id=source_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))


# @bp.route("/delete_form_field/<workflow_id>/<form_field_id>/", methods=["GET", "POST"])
# def delete_form_field_view(workflow_id: int, form_field_id: int) -> Union[str, Response]:
#     """Delete a form field."""
#     manager = get_db_manager()
#     manager.form_fields.delete(form_field_id)
#     return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
