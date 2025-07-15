"""Define sql views."""

from typing import Union

from flask import Blueprint, redirect, render_template, url_for
from werkzeug.wrappers.response import Response

from dashboard.database import get_db_manager

from ...forms import (
    CreateRecordSetSourceForm,
    CreateRecordSetTransposeSourceForm,
    CreateRecordSourceForm,
)

bp = Blueprint("sql", __name__)


@bp.route("/workflow/<workflow_id>/add_sql_record_source", methods=["GET", "POST"])
def add_record_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record source view."""
    form = CreateRecordSourceForm()

    manager = get_db_manager()
    database_choices = manager.database_meta_sources.get_all()
    form.database.choices = [(db.DatabaseId, db.Name) for db in database_choices]

    if form.validate_on_submit():
        source_type = manager.source_types.get_from_name(name="SQL Record")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            step=form.step.data or 1,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_source.html", form=form, workflow_id=workflow_id
    )


@bp.route("/workflow/<workflow_id>/add_sql_record_set_source", methods=["GET", "POST"])
def add_record_set_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateRecordSetSourceForm()
    manager = get_db_manager()
    database_choices = manager.database_meta_sources.get_all()
    form.database.choices = [(db.DatabaseId, db.Name) for db in database_choices]

    if form.validate_on_submit():
        splitter = form.splitter_choice.data == "splitter"

        source_type = manager.source_types.get_from_name(name="SQL RecordSet")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            field_name=form.field_name.data,
            splitter=splitter,
            step=form.step.data or 1,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_set_source.html", form=form, workflow_id=workflow_id
    )


@bp.route("/workflow/<workflow_id>/add_sql_record_set_transpose_source", methods=["GET", "POST"])
def add_record_set_transpose_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateRecordSetTransposeSourceForm()
    manager = get_db_manager()
    database_choices = manager.database_meta_sources.get_all()
    form.database.choices = [(db.DatabaseId, db.Name) for db in database_choices]

    if form.validate_on_submit():
        source_type = manager.source_types.get_from_name(name="SQL RecordSet Transpose")
        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            key_field=form.key_field.data,
            value_field=form.value_field.data,
            step=form.step.data or 1,
        )
        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_set_transpose_source.html", form=form, workflow_id=workflow_id
    )
