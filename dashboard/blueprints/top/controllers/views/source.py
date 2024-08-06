"""Define source views."""

from ...models import delete_source, delete_form_field
from werkzeug.wrappers.response import Response
from flask import Blueprint, redirect, url_for

from typing import Union

bp = Blueprint("source", __name__)


@bp.route("/delete_source/<workflow_id>/<source_id>", methods=["GET", "POST"])
def delete_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
    """Delete a source."""
    delete_source(source_id=source_id)
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))


@bp.route("/delete_form_field/<workflow_id>/<form_field_id>/", methods=["GET", "POST"])
def delete_form_field_view(workflow_id: int, form_field_id: int) -> Union[str, Response]:
    """Delete a form field."""
    delete_form_field(form_field_id=form_field_id)
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
