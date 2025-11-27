"""Define Text views."""

from typing import Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

from ...forms import CreateTextOutcomeForm
from ...models import get_optional_new_file_template_id

bp = Blueprint("text", __name__)


@bp.route("/workflow/<workflow_id>/add_text_outcome", methods=["GET", "POST"])
def add_text_outcome_view(workflow_id: int) -> Union[str, Response]:
    """Add a Text File outcome document."""
    form = CreateTextOutcomeForm()
    manager = get_db_manager()

    if form.validate_on_submit():
        name = form.name.data

        if name and manager.sources.name_exists(name=name):
            flash(f"{name} already exists, choose another name", "error")
            return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        input_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=int(request.form["option"]),
            location=form.location.data,
            bucket=form.bucket.data,
        )

        output_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=int(request.form["outputoption"]),
            location=form.output_location.data,
            bucket=form.output_bucket.data,
        )

        outcome_type = manager.outcome_types.get_from_name(name="Text")
        manager.outcomes.add(
            workflow_id=workflow_id,
            outcome_type=outcome_type,
            name=name,
            input_instance_id=input_file_template_id,
            output_instance_id=output_file_template_id,
            download_name=form.download_name.data,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    storage_instances = manager.storage_instances.get_all()

    return render_template(
        "top/add_outcome/add_text_outcome.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
    )
