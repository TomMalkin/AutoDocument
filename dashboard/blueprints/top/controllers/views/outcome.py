"""Define outcome views."""

from typing import Union

from flask import Blueprint, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.blueprints.top.models import (
    file_template_required,
    get_optional_new_file_template_id,
)
from dashboard.database import get_db_manager

from .outcome_form_factory import create_outcome_form

bp = Blueprint("outcome", __name__)


@bp.route("/delete_outcome/<workflow_id>/<outcome_id>", methods=["GET", "POST"])
def delete_outcome_view(workflow_id: int, outcome_id: int) -> Union[str, Response]:
    """Delete a outcome."""
    manager = get_db_manager()
    manager.outcomes.delete(outcome_id=outcome_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))


@bp.route("/add_outcome/<workflow_id>/<outcome_type_id>", methods=["GET", "POST"])
def add_outcome_view(workflow_id: int, outcome_type_id: int) -> Union[str, Response]:
    """Add an outcome."""
    manager = get_db_manager()
    outcome_type = manager.outcome_types.get(outcome_type_id=outcome_type_id)

    logger.info(f"Adding outcome with {outcome_type_id=}")

    form = create_outcome_form(manager=manager, outcome_type=outcome_type)

    if form.validate_on_submit():
        name = form.name.data
        download_name = form.download_name.data
        logger.info(f"Form valid with {name=} and {download_name=}")

        # Handle input file template
        input_storage_instance_id = int(request.form.get("option", -1))
        input_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=input_storage_instance_id,
            location=form.location.data,
            bucket=form.bucket.data,
        )
        file_upload = file_template_required(
            input_storage_instance_id
        )

        logger.info(f"{input_storage_instance_id=}, {input_file_template_id=}, {file_upload=}")

        output_storage_instance_id = int(request.form.get("outputoption", -1))
        output_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=output_storage_instance_id,
            location=form.output_location.data,
            bucket=form.output_bucket.data,
        )
        logger.info(f"{output_storage_instance_id=}, {output_file_template_id=}")

        manager.outcomes.add(
            workflow_id=workflow_id,
            outcome_type=outcome_type,
            name=name,
            input_instance_id=input_file_template_id,
            output_instance_id=output_file_template_id,
            download_name=download_name,
            file_upload=file_upload,  # Mark as file upload if an input file is specified
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(f"Form errors for adding outcome: {form.errors}")

    storage_instances = manager.storage_instances.get_all()

    components = []
    if outcome_type.IsFile:
        components.append("input_file_accessor")
        components.append("output_file_accessor")

    explanations = [
        f"Add a {outcome_type.Name} outcome.",
        "Define the template to use and where to save the generated file(s).",
    ]

    return render_template(
        "top/add_outcome.html",
        form=form,
        workflow_id=workflow_id,
        outcome_type_id=outcome_type_id,
        storage_instances=storage_instances,  # Passed for the dynamic file access forms
        components=components,
        explanations=explanations,
        title=f"Add {outcome_type.Name} Outcome",
        placeholder="outcome.pdf",  # TODO: per outcome type placeholders
    )


@bp.route("/workflow/<int:workflow_id>/outcome/<int:outcome_id>/edit", methods=["GET", "POST"])
def edit_outcome_view(workflow_id: int, outcome_id: int) -> Union[str, Response]:
    """Edit an existing outcome."""
    manager = get_db_manager()
    outcome = manager.outcomes.get(outcome_id=outcome_id)
    outcome_type = outcome.outcome_type

    if request.method == "POST":
        form = create_outcome_form(manager=manager, outcome_type=outcome_type)
    else:
        initial_data = {
            "name": outcome.Name,
            "download_name": outcome.DownloadName,
            # Add other fields if they become editable
        }
        if outcome.input_file_template:
            initial_data["location"] = outcome.input_file_template.Location
            initial_data["bucket"] = outcome.input_file_template.Bucket
            # 'option' will be set by the hx-trigger="load" in the template
            initial_data["option"] = outcome.input_file_template.StorageInstanceId
        if outcome.output_file_template:
            initial_data["output_location"] = outcome.output_file_template.Location
            initial_data["output_bucket"] = outcome.output_file_template.Bucket
            # 'outputoption' will be set by the hx-trigger="load" in the template
            initial_data["outputoption"] = outcome.output_file_template.StorageInstanceId

        form = create_outcome_form(
            manager=manager, outcome_type=outcome_type, initial_data=initial_data
        )

    if form.validate_on_submit():
        name = form.name.data
        download_name = form.download_name.data

        # Handle input file template
        input_storage_instance_id = int(request.form.get("option", -1))
        input_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=input_storage_instance_id,
            location=form.location.data,
            bucket=form.bucket.data,
        )
        file_upload = file_template_required(input_storage_instance_id)

        # Handle output file template
        output_storage_instance_id = int(request.form.get("outputoption", -1))
        output_file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=output_storage_instance_id,
            location=form.output_location.data,
            bucket=form.output_bucket.data,
        )

        manager.outcomes.update(
            outcome_id=outcome_id,
            name=name,
            input_file_template_id=input_file_template_id,
            output_file_template_id=output_file_template_id,
            download_name=download_name,
            file_upload=file_upload,
        )
        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(f"Form errors for editing outcome: {form.errors}")

    storage_instances = manager.storage_instances.get_all()
    components = []
    if outcome_type.IsFile:
        components.append("input_file_accessor")
        components.append("output_file_accessor")

    explanations = [
        f"Edit the {outcome_type.Name} outcome.",
        "Modify the template details and where the generated file(s) will be saved.",
    ]

    return render_template(
        "top/edit_outcome.html",
        form=form,
        workflow_id=workflow_id,
        outcome_id=outcome_id,
        outcome=outcome,
        storage_instances=storage_instances,
        components=components,
        explanations=explanations,
        title=f"Edit Outcome: {outcome_type.Name}",
        placeholder="outcome.pdf"
    )
