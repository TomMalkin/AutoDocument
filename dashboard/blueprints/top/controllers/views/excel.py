"""Define excel views."""

from typing import Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.blueprints.top.models import get_optional_new_file_template_id
from dashboard.database import get_db_manager

from ...forms import CreateExcelRecordSourceForm, CreateExcelTableSourceForm

bp = Blueprint("excel", __name__)


@bp.route("/workflow/<workflow_id>/add_excel_record_source", methods=["GET", "POST"])
def add_excel_record_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateExcelRecordSourceForm()
    manager = get_db_manager()

    if form.validate_on_submit():
        location = form.location.data
        bucket = form.bucket.data
        name = form.name.data
        header_row = form.header_row.data
        sheet_name = form.sheet_name.data
        step = form.step.data or 1
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

        source_type = manager.source_types.get_from_name(name="ExcelRecord")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            step=step,
            file_template_id=file_template_id,
            name=name,
            header_row=header_row,
            sheet_name=sheet_name,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    else:
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()

    return render_template(
        "top/add_source/add_excel_record_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
    )


@bp.route("/workflow/<workflow_id>/add_excel_table_source", methods=["GET", "POST"])
def add_excel_table_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateExcelTableSourceForm()
    manager = get_db_manager()

    if form.validate_on_submit():

        name = form.name.data
        step = form.step.data or 1
        location = form.location.data
        bucket = form.bucket.data
        field_name = form.field_name.data
        header_row = form.header_row.data
        sheet_name = form.sheet_name.data
        splitter = form.splitter_choice.data == "splitter"
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

        source_type = manager.source_types.get_from_name(name="ExcelTable")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            splitter=splitter,
            field_name=field_name,
            sheet_name=sheet_name,
            header_row=header_row,
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
        "top/add_source/add_excel_table_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
    )
