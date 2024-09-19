"""Define workflow views."""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from loguru import logger
from ...forms import CreateCSVRecordSourceForm, CreateCSVTableSourceForm
from ...models import add_csv_table_source, add_csv_record_source, get_file_accessors
from werkzeug.wrappers.response import Response
from dashboard.database import get_manager

from typing import Union

bp = Blueprint("csv", __name__)


@bp.route("/workflow/<workflow_id>/add_csv_record_source", methods=["GET", "POST"])
def add_csv_record_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateCSVRecordSourceForm()

    if form.validate_on_submit():
        named_orientation = "horizontal" if form.orientation.data != '1' else "vertical"
        logger.info(f"{form.orientation.data=}")

        location = form.location.data
        bucket = form.bucket.data
        name = form.name.data

        if name:
            sql = "select Name from Source where WorkflowId = :workflow_id"
            params = {"workflow_id": workflow_id}
            current_names = get_manager().db.recordset(sql=sql, params=params).column("Name")

            if name in current_names:
                logger.info(f"attempted add of {name} when existing names are {current_names}")
                flash(f"{name} already exists, choose another name", "error")
                return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_access_id = None

        if request.form["option"]:
            file_access_id = int(request.form["option"])
            if file_access_id == -1:
                file_access_id = None

        add_csv_record_source(
            workflow_id=workflow_id,
            orientation=named_orientation,
            step=form.step.data,
            location=location,
            bucket=bucket,
            file_access_id=file_access_id,
            name=name,
        )

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    else:
        logger.error(form.errors)

    file_access_list = get_file_accessors()

    return render_template(
        "top/add_source/add_csv_record_source.html",
        form=form,
        workflow_id=workflow_id,
        file_access_list=file_access_list,
    )


@bp.route("/workflow/<workflow_id>/add_csv_table_source", methods=["GET", "POST"])
def add_csv_table_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateCSVTableSourceForm()

    if form.validate_on_submit():

        location = form.location.data
        bucket = form.bucket.data
        name = form.name.data

        if name:
            sql = "select Name from Source where WorkflowId = :workflow_id"
            params = {"workflow_id": workflow_id}
            current_names = get_manager().db.recordset(sql=sql, params=params).column("Name")

            if name in current_names:
                logger.info(f"attempted add of {name} when existing names are {current_names}")
                flash(f"{name} already exists, choose another name", "error")
                return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_access_id = None

        if request.form["option"]:
            file_access_id = int(request.form["option"])
            if file_access_id == -1:
                file_access_id = None

        splitter = form.splitter_choice.data == "splitter"

        add_csv_table_source(
            workflow_id=workflow_id,
            field_name=form.field_name.data,
            splitter=splitter,
            step=form.step.data,
            location=location,
            bucket=bucket,
            file_access_id=file_access_id,
            name=name,
        )
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    file_access_list = get_file_accessors()
    return render_template(
        "top/add_source/add_csv_table_source.html",
        form=form,
        workflow_id=workflow_id,
        file_access_list=file_access_list,
    )
