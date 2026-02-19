"""Define form views."""

from typing import Union, cast

from flask import Blueprint, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

from ...forms import CreateFormFieldForm

bp = Blueprint("form_field", __name__)


@bp.route("/workflow/<workflow_id>/add_form_field", methods=["GET", "POST"])
def add_form_field_view(workflow_id: int) -> Union[str, Response]:
    """Add a form field source to a workflow."""
    form = CreateFormFieldForm()

    manager = get_db_manager()

    if form.validate_on_submit():
        cast(str, form.field_type.data)

        manager.form_fields.add(
            workflow_id=workflow_id,
            name=cast(str, form.name.data),
            label=cast(str, form.label.data),
            field_type=cast(str, form.field_type.data),
        )
        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    return render_template("top/add_form_field_source.html", form=form, workflow_id=workflow_id)


@bp.route("/delete_form_field/<workflow_id>/<form_field_id>/", methods=["GET", "POST"])
def delete_form_field_view(workflow_id: int, form_field_id: int) -> Union[str, Response]:
    """Delete a form field."""
    manager = get_db_manager()
    manager.form_fields.delete(form_field_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
