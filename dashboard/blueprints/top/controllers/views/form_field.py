"""Define workflow views."""

from flask import Blueprint, render_template, redirect, url_for
from ...forms import CreateFormFieldForm
from ...models import add_form_field_source
from werkzeug.wrappers.response import Response
from loguru import logger

from typing import Union

bp = Blueprint("form_field", __name__)


@bp.route("/workflow/<workflow_id>/add_form_field", methods=["GET", "POST"])
def add_form_field_view(workflow_id: int) -> Union[str, Response]:
    """Add a form field source to a workflow."""
    form = CreateFormFieldForm()

    if form.validate_on_submit():
        add_form_field_source(
            workflow_id=workflow_id,
            name=form.name.data,
            label=form.label.data,
            field_type=form.field_type.data,
        )
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
    else:
        logger.info(form.errors)

    return render_template("top/add_source/add_form_field_source.html", form=form, workflow_id=workflow_id)
