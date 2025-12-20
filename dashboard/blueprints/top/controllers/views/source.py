"""Define source views."""

from typing import Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from dashboard.constants import EXPLANATION_MAP
from dashboard.database import get_db_manager

from ...models import get_optional_new_file_template_id
from .source_form_factory import create_source_form

bp = Blueprint("source", __name__)


@bp.route("/delete_source/<workflow_id>/<source_id>", methods=["GET", "POST"])
def delete_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
    """Delete a source."""
    manager = get_db_manager()
    manager.sources.delete(source_id=source_id)
    manager.commit()
    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))


@bp.route("/add_source/<workflow_id>/<source_type_id>", methods=["GET", "POST"])
def add_source_view(workflow_id: int, source_type_id: int) -> Union[str, Response]:
    """Add a source view."""
    manager = get_db_manager()
    source_type = manager.source_types.get(source_type_id=source_type_id)

    form = create_source_form(manager=manager, source_type=source_type)

    if form.validate_on_submit():
        name = location = bucket = storage_instance_id = file_template_id = None
        step = int(form.step.data)

        named_orientation = None
        if hasattr(form, "orientation"):
            named_orientation = "horizontal" if form.orientation.data != "1" else "vertical"

        name = location = bucket = storage_instance_id = file_template_id = None
        if form.is_file:
            name = form.name.data
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

        sql_text = database_id = None
        if hasattr(form, "database"):
            sql_text = form.sql_text.data
            database_id = int(form.database.data)

        splitter = field_name = None
        if hasattr(form, "splitter_choice"):
            splitter = form.splitter_choice.data == "splitter"
            field_name = form.field_name.data

        key_field = value_field = None
        if hasattr(form, "key_field"):
            key_field = form.key_field.data
            value_field = form.value_field.data

        header_row = sheet_name = None
        if hasattr(form, "header_row"):
            header_row = form.header_row.data
            sheet_name = form.sheet_name.data

        llm = prompt_template = system_prompt = None
        if hasattr(form, "llm"):
            llm_id = form.llm.data
            field_name = form.llm_field_name.data
            prompt_template = form.prompt_template.data
            system_prompt = form.system_prompt.data

            source_type = manager.source_types.get_from_name(name="LLM")

            llm = None
            if llm_id:
                llm = manager.llms.get(llm_id=int(llm_id))

        manager.sources.add(
            workflow_id=workflow_id,
            source_type=source_type,
            step=step,
            file_template_id=file_template_id,
            name=name,
            database_id=database_id,
            sql_text=sql_text,
            splitter=splitter,
            field_name=field_name,
            key_field=key_field,
            value_field=value_field,
            orientation=named_orientation,
            sheet_name=sheet_name,
            header_row=header_row,
            llm=llm,
            llm_prompt_template=prompt_template,
            llm_system_prompt=system_prompt,
        )
        manager.commit()

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()

    components = []
    if form.is_file:
        components.append("file_accessor")

    if source_type.IsMulti:
        components.append("splitter")

    explanations = EXPLANATION_MAP.get(source_type.Name) or []

    return render_template(
        "top/add_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
        components=components,
        explanations=explanations,
        source_type_id=source_type_id,
        title=f"Add Source: {source_type.Name}"
    )


@bp.route("/workflow/<int:workflow_id>/source/<int:source_id>/edit", methods=["GET", "POST"])
def edit_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
    """Edit a source."""
    manager = get_db_manager()
    source = manager.sources.get(source_id=source_id)
    source_type = source.source_type

    if request.method == "POST":
        form = create_source_form(manager=manager, source_type=source_type)
    else:
        initial_data = {
            "step": source.Step,
            "name": source.Name,
            "database": source.DatabaseId,
            "sql_text": source.SQLText,
            "splitter_choice": "splitter" if source.Splitter else "field",
            "field_name": source.FieldName,
            "key_field": source.KeyField,
            "value_field": source.ValueField,
            "orientation": "1" if source.Orientation == "vertical" else "0",
            "sheet_name": source.SheetName,
            "header_row": source.HeaderRow,
            "llm": source.LLMId,
            "llm_field_name": source.FieldName,
            "prompt_template": source.LLMPromptTemplate,
            "system_prompt": source.LLMSystemPrompt,
        }
        if source.file_template:
            initial_data["location"] = source.file_template.Location
            initial_data["bucket"] = source.file_template.Bucket

        form = create_source_form(
            manager=manager, source_type=source_type, initial_data=initial_data
        )

    if form.validate_on_submit():
        step = int(form.step.data)

        named_orientation = None
        if hasattr(form, "orientation"):
            named_orientation = "horizontal" if form.orientation.data != "1" else "vertical"

        name = location = bucket = storage_instance_id = file_template_id = None
        if form.is_file:
            name = form.name.data
            location = form.location.data
            bucket = form.bucket.data
            storage_instance_id = int(request.form["option"])

            # Check for name collision, excluding the current source
            existing_source = manager.sources.get_by_name(name=name)
            if existing_source and existing_source.Id != source_id:
                flash(f"{name} already exists, choose another name", "error")
                return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

            file_template_id = get_optional_new_file_template_id(
                manager=manager,
                storage_instance_id=storage_instance_id,
                location=location,
                bucket=bucket,
            )

        sql_text = database_id = None
        if hasattr(form, "database"):
            sql_text = form.sql_text.data
            database_id = int(form.database.data)

        splitter = field_name = None
        if hasattr(form, "splitter_choice"):
            splitter = form.splitter_choice.data == "splitter"
            if not splitter:
                field_name = form.field_name.data

        key_field = value_field = None
        if hasattr(form, "key_field"):
            key_field = form.key_field.data
            value_field = form.value_field.data

        header_row = sheet_name = None
        if hasattr(form, "header_row"):
            header_row = form.header_row.data
            sheet_name = form.sheet_name.data

        llm = None
        llm_prompt_template = llm_system_prompt = None
        if hasattr(form, "llm"):
            llm_id = form.llm.data
            field_name = form.llm_field_name.data
            llm_prompt_template = form.prompt_template.data
            llm_system_prompt = form.system_prompt.data
            if llm_id:
                llm = manager.llms.get(llm_id=int(llm_id))

        manager.sources.update(
            source_id=source_id,
            step=step,
            file_template_id=file_template_id,
            name=name,
            database_id=database_id,
            sql_text=sql_text,
            splitter=splitter or False,
            field_name=field_name,
            key_field=key_field,
            value_field=value_field,
            orientation=named_orientation,
            sheet_name=sheet_name,
            header_row=header_row,
            llm=llm,
            llm_prompt_template=llm_prompt_template,
            llm_system_prompt=llm_system_prompt,
        )
        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()
    components = ["file_accessor"] if form.is_file else []
    if source_type.IsMulti:
        components.append("splitter")

    explanations = EXPLANATION_MAP.get(source_type.Name) or []

    return render_template(
        "top/edit_source.html",
        form=form,
        workflow_id=workflow_id,
        source_id=source_id,
        storage_instances=storage_instances,
        components=components,
        explanations=explanations,
        title=f"Edit Source: {source_type.Name}",
        source=source,
    )
