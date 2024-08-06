"""Define workflow views."""

from flask import Blueprint, render_template, redirect, url_for
from ...forms import (
    CreateRecordSourceForm,
    CreateRecordSetSourceForm,
    CreateRecordSetTransposeSourceForm,
)
from ...models import (
    get_meta_database_choices,
    add_record_source,
    add_record_set_source,
    add_record_set_transpose_source,
)
from werkzeug.wrappers.response import Response

from typing import Union

bp = Blueprint("sql", __name__)


@bp.route("/workflow/<workflow_id>/add_sql_record_source", methods=["GET", "POST"])
def add_record_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record source view."""
    form = CreateRecordSourceForm()
    form.database.choices = get_meta_database_choices()

    if form.validate_on_submit():
        add_record_source(
            workflow_id=workflow_id,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            step=form.step.data,
        )
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_source.html", form=form, workflow_id=workflow_id
    )


@bp.route("/workflow/<workflow_id>/add_sql_record_set_source", methods=["GET", "POST"])
def add_record_set_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateRecordSetSourceForm()
    form.database.choices = get_meta_database_choices()

    if form.validate_on_submit():
        splitter = form.splitter_choice.data == "splitter"

        add_record_set_source(
            workflow_id=workflow_id,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            field_name=form.field_name.data,
            splitter=splitter,
            step=form.step.data,
        )
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_set_source.html", form=form, workflow_id=workflow_id
    )


@bp.route("/workflow/<workflow_id>/add_sql_record_set_transpose_source", methods=["GET", "POST"])
def add_record_set_transpose_source_view(workflow_id: int) -> Union[str, Response]:
    """Add a record set source view."""
    form = CreateRecordSetTransposeSourceForm()
    form.database.choices = get_meta_database_choices()

    if form.validate_on_submit():
        add_record_set_transpose_source(
            workflow_id=workflow_id,
            sql_text=form.sql_text.data,
            database_id=form.database.data,
            key_field=form.key_field.data,
            value_field=form.value_field.data,
            step=form.step.data,
        )
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return render_template(
        "top/add_source/add_record_set_transpose_source.html", form=form, workflow_id=workflow_id
    )
