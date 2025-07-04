"""Define Microsoft Word views."""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from ...forms import CreateWordOutcomeForm

# from ...models import get_file_accessors, add_word_outcome
from ...models import get_optional_new_file_template_id
from werkzeug.wrappers.response import Response
from dashboard.database import get_db_manager

from typing import Union

bp = Blueprint("word", __name__)


@bp.route("/workflow/<workflow_id>/add_word_outcome", methods=["GET", "POST"])
def add_word_outcome_view(workflow_id: int) -> Union[str, Response]:
    """Add a Microsoft Word outcome."""
    form = CreateWordOutcomeForm()
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

        outcome_type = manager.outcome_types.get_from_name(name="Microsoft Word")
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
        "top/add_outcome/add_word_outcome.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
    )
