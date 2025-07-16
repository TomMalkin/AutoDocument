"""Define csv views."""

from typing import Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

from ...forms import CreateCSVRecordSourceForm, CreateCSVTableSourceForm
from ...models import get_optional_new_file_template_id

bp = Blueprint("csv", __name__)


@bp.route("/workflow/<workflow_id>/add_csv_record_source", methods=["GET", "POST"])
def add_csv_record_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateCSVRecordSourceForm()
    manager = get_db_manager()

    if form.validate_on_submit():
        named_orientation = "horizontal" if form.orientation.data != "1" else "vertical"
        logger.info(f"{form.orientation.data=}")

        name = form.name.data
        step = form.step.data or 1
        location = form.location.data
        bucket = form.bucket.data
        storage_instance_id = int(request.form["option"])

        if name and manager.sources.name_exists(name=name):
            flash(f"{name} already exists, choose another name", "error")
            return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=storage_instance_id,
            location=location,
            bucket=bucket,
        )

        source_type = manager.source_types.get_from_name(name="CSVRecord")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            orientation=named_orientation,
            step=step,
            file_template_id=file_template_id,
            name=name,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()

    return render_template(
        "top/add_source/add_csv_record_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
    )


@bp.route("/workflow/<workflow_id>/add_csv_table_source", methods=["GET", "POST"])
def add_csv_table_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateCSVTableSourceForm()
    manager = get_db_manager()

    if form.validate_on_submit():

        name = form.name.data
        step = form.step.data or 1
        location = form.location.data
        bucket = form.bucket.data
        field_name = form.field_name.data
        storage_instance_id = int(request.form["option"])
        splitter = form.splitter_choice.data == "splitter"

        if name and manager.sources.name_exists(name=name):
            flash(f"{name} already exists, choose another name", "error")
            return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_template_id = get_optional_new_file_template_id(
            manager=manager,
            storage_instance_id=storage_instance_id,
            location=location,
            bucket=bucket,
        )

        source_type = manager.source_types.get_from_name(name="CSVTable")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            splitter=splitter,
            field_name=field_name,
            step=step,
            file_template_id=file_template_id,
            name=name,
        )
        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()
    return render_template(
        "top/add_source/add_csv_table_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances
    )
