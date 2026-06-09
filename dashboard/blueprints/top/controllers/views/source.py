"""Define source views."""

from typing import Optional, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from loguru import logger
from werkzeug.wrappers.response import Response

from autodoc.data.tables import CSVSource, DatabaseSource, ExcelSource, LLMSource, Source
from dashboard.constants import EXPLANATION_MAP
from dashboard.database import get_db_manager

from ...models import get_optional_new_file_template_id
from .source_form_factory import create_source_form

bp = Blueprint("source", __name__)


def _field_name_missing(form) -> bool:
    """Return if there is an issue with the field name missing if a multi source."""
    logger.debug("Checking if field name is missing")
    if not (hasattr(form, "splitter_choice") and hasattr(form, "field_name")):
        logger.debug("splitter_choice and/or field_name is missing from form, ignoring")
        return False

    logger.debug("splitter_choice is {}, field_name is {}", form.splitter_choice.data, form.field_name.data)

    if form.splitter_choice.data == "field" and not form.field_name.data:
        logger.debug("Splitter set to field and no field name, flagging")
        return True

    logger.debug("Field FieldName check ok")
    return False


def _get_file_template_id(manager, form) -> Optional[int]:
    """Get a file template from a form."""
    return get_optional_new_file_template_id(
        manager=manager,
        storage_instance_id=int(request.form["option"]),
        location=form.location.data,
        bucket=form.bucket.data,
    )


def _build_components(form, source_type):
    components = []
    if form.is_file:
        components.append("file_accessor")
    if source_type.IsMulti:
        components.append("splitter")
    return components


def _get_initial_data(source: Source) -> dict:
    """Build the initial data sent to the form when editting."""
    data: dict = {
        "step": source.Step,
        "name": source.Name,
    }

    match source:
        case CSVSource():
            data |= {
                "splitter_choice": "splitter" if source.IsSplitter else "field",
                "field_name": source.FieldName,
                "location": source.file_template.Location if source.file_template else None,
                "bucket": source.file_template.Bucket if source.file_template else None,
            }
        case ExcelSource():
            data |= {
                "splitter_choice": "splitter" if source.IsSplitter else "field",
                "field_name": source.FieldName,
                "sheet_name": source.SheetName,
                "header_row": source.HeaderRow,
                "location": source.file_template.Location if source.file_template else None,
                "bucket": source.file_template.Bucket if source.file_template else None,
            }
        case DatabaseSource():
            data |= {
                "database": source.DatabaseId,
                "sql_text": source.SQLText,
                "splitter_choice": "splitter" if source.IsSplitter else "field",
                "field_name": source.FieldName,
            }
        case LLMSource():
            data |= {
                "llm": source.LLMId,
                "prompt_template": source.LLMPromptTemplate,
                "system_prompt": source.LLMSystemPrompt,
            }
        case _:
            raise ValueError(f"Unknown source type: {type(source)}")

    logger.debug("initial data calculated as {}", data)

    return data


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
        step = int(form.step.data)
        name = form.name.data if form.is_file else None

        logger.debug(form.data)

        if name and manager.sources.name_exists(name=name, workflow_id=workflow_id):
            flash(f"{name} already exists, choose another name", "error")
            return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_template_id: Optional[int] = _get_file_template_id(manager, form) if form.is_file else None

        if _field_name_missing(form):
            flash("A Field Name is required when setting to Field", "error")
            return redirect(
                url_for(
                    "top.source.add_source_view",
                    workflow_id=workflow_id,
                    source_type_id=source_type_id,
                )
            )

        match source_type.Name:
            case "CSV":
                manager.sources.add_csv(
                    workflow_id=workflow_id,
                    source_type=source_type,
                    step=step,
                    name=name,
                    file_template_id=file_template_id,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                )
            case "Excel":
                manager.sources.add_excel(
                    workflow_id=workflow_id,
                    source_type=source_type,
                    step=step,
                    name=name,
                    file_template_id=file_template_id,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                    sheet_name=form.sheet_name.data,
                    header_row=form.header_row.data,
                )
            case "Database":
                manager.sources.add_database(
                    workflow_id=workflow_id,
                    source_type=source_type,
                    step=step,
                    name=name,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                    database_id=int(form.database.data),
                    sql_text=form.sql_text.data,
                )
            case "LLM":
                llm = manager.llms.get(llm_id=int(form.llm.data)) if form.llm.data else None
                if not llm:
                    flash("Please select an LLM", "error")
                    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

                manager.sources.add_llm(
                    workflow_id=workflow_id,
                    source_type=source_type,
                    step=step,
                    name=name,
                    llm=llm,
                    llm_prompt_template=form.prompt_template.data,
                    llm_system_prompt=form.system_prompt.data,
                )
            case _:
                raise ValueError(f"Unknown source type: {source_type.Name}")

        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    title_mapper = {
        "CSV": "CSV",
        "Excel": "Excel",
        "LLM": "AI Response",
        "Database": "Database Query",
    }

    storage_instances = manager.storage_instances.get_all()
    components = _build_components(form, source_type)

    explanations = EXPLANATION_MAP.get(source_type.Name) or []
    _title = title_mapper.get(source_type.Name, source_type.Name)

    return render_template(
        "top/add_source.html",
        form=form,
        workflow_id=workflow_id,
        storage_instances=storage_instances,
        components=components,
        explanations=explanations,
        source_type_id=source_type_id,
        title=f"Add Source: {_title}",
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
        form = create_source_form(manager, source_type=source_type, initial_data=_get_initial_data(source))

    if form.validate_on_submit():
        step = int(form.step.data)
        name = form.name.data if form.is_file else None

        logger.debug(form.data)

        if form.is_file and name:
            existing_source = manager.sources.get_by_name_in_workflow(name=name, workflow_id=workflow_id)

            # if existing_source:
            #     logger.debug("Checking if there is an existing source on this workflow with this name already.")
            #     logger.debug("Existing Source found with Source Id {} and WorkflowId {}")

            if existing_source and existing_source.Id != source_id and existing_source.WorkflowId == workflow_id:  # Checking if there is a name overlap
                flash(f"{name} already exists, choose another name", "error")
                return redirect(url_for("top.source.edit_source_view", workflow_id=workflow_id, source_id=source_id))

        file_template_id = _get_file_template_id(manager, form) if form.is_file else None

        if _field_name_missing(form):
            flash("A Field Name is required when setting to Field", "error")
            return redirect(url_for("top.source.edit_source_view", workflow_id=workflow_id, source_id=source_id))

        match source_type.Name:
            case "CSV":
                manager.sources.update_csv(
                    source_id=source_id,
                    step=step,
                    name=name,
                    file_template_id=file_template_id,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                )
            case "Excel":
                manager.sources.update_excel(
                    source_id=source_id,
                    step=step,
                    name=name,
                    file_template_id=file_template_id,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                    sheet_name=form.sheet_name.data,
                    header_row=form.header_row.data,
                )
            case "Database":
                manager.sources.update_database(
                    source_id=source_id,
                    step=step,
                    name=name,
                    is_splitter=form.splitter_choice.data == "splitter",
                    field_name=form.field_name.data,
                    database_id=int(form.database.data),
                    sql_text=form.sql_text.data,
                )
            case "LLM":
                llm = manager.llms.get(llm_id=int(form.llm.data)) if form.llm.data else None
                if not llm:
                    flash("Please select an LLM", "error")
                    return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
                manager.sources.update_llm(
                    source_id=source_id,
                    step=step,
                    name=name,
                    llm=llm,
                    llm_prompt_template=form.prompt_template.data,
                    llm_system_prompt=form.system_prompt.data,
                )
            case _:
                raise ValueError(f"Unknown source type: {source_type.Name}")

        manager.commit()
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    elif request.method == "POST":
        logger.error(form.errors)

    storage_instances = manager.storage_instances.get_all()
    components = _build_components(form, source_type)

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


# @bp.route("/workflow/<int:workflow_id>/source/<int:source_id>/edit", methods=["GET", "POST"])
# def edit_source_view(workflow_id: int, source_id: int) -> Union[str, Response]:
#     """Edit a source."""
#     manager = get_db_manager()
#     source = manager.sources.get(source_id=source_id)
#     source_type = source.source_type
#
#     if request.method == "POST":
#         form = create_source_form(manager=manager, source_type=source_type)
#     else:
#         initial_data = {
#             "step": source.Step,
#             "name": source.Name,
#             "database": source.DatabaseId,
#             "sql_text": source.SQLText,
#             "splitter_choice": "splitter" if source.Splitter else "field",
#             "field_name": source.FieldName,
#             "key_field": source.KeyField,
#             "value_field": source.ValueField,
#             "orientation": "1" if source.Orientation == "vertical" else "0",
#             "sheet_name": source.SheetName,
#             "header_row": source.HeaderRow,
#             "llm": source.LLMId,
#             "llm_field_name": source.FieldName,
#             "prompt_template": source.LLMPromptTemplate,
#             "system_prompt": source.LLMSystemPrompt,
#         }
#         if source.file_template:
#             initial_data["location"] = source.file_template.Location
#             initial_data["bucket"] = source.file_template.Bucket
#
#         form = create_source_form(manager=manager, source_type=source_type, initial_data=initial_data)
#
#     if form.validate_on_submit():
#         step = int(form.step.data)
#
#         named_orientation = None
#         if hasattr(form, "orientation"):
#             named_orientation = "horizontal" if form.orientation.data != "1" else "vertical"
#
#         name = location = bucket = storage_instance_id = file_template_id = None
#         if form.is_file:
#             name = form.name.data
#             location = form.location.data
#             bucket = form.bucket.data
#             storage_instance_id = int(request.form["option"])
#
#             # Check for name collision, excluding the current source
#             existing_source = manager.sources.get_by_name(name=name)
#             if existing_source and existing_source.Id != source_id:
#                 flash(f"{name} already exists, choose another name", "error")
#                 return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
#
#             file_template_id = get_optional_new_file_template_id(
#                 manager=manager,
#                 storage_instance_id=storage_instance_id,
#                 location=location,
#                 bucket=bucket,
#             )
#
#         sql_text = database_id = None
#         if hasattr(form, "database"):
#             sql_text = form.sql_text.data
#             database_id = int(form.database.data)
#
#         splitter = field_name = None
#         if hasattr(form, "splitter_choice"):
#             splitter = form.splitter_choice.data == "splitter"
#             if not splitter:
#                 field_name = form.field_name.data
#
#         key_field = value_field = None
#         if hasattr(form, "key_field"):
#             key_field = form.key_field.data
#             value_field = form.value_field.data
#
#         header_row = sheet_name = None
#         if hasattr(form, "header_row"):
#             header_row = form.header_row.data
#             sheet_name = form.sheet_name.data
#
#         llm = None
#         llm_prompt_template = llm_system_prompt = None
#         if hasattr(form, "llm"):
#             llm_id = form.llm.data
#             field_name = form.llm_field_name.data
#             llm_prompt_template = form.prompt_template.data
#             llm_system_prompt = form.system_prompt.data
#             if llm_id:
#                 llm = manager.llms.get(llm_id=int(llm_id))
#
#         manager.sources.update(
#             source_id=source_id,
#             step=step,
#             file_template_id=file_template_id,
#             name=name,
#             database_id=database_id,
#             sql_text=sql_text,
#             splitter=splitter or False,
#             field_name=field_name,
#             key_field=key_field,
#             value_field=value_field,
#             orientation=named_orientation,
#             sheet_name=sheet_name,
#             header_row=header_row,
#             llm=llm,
#             llm_prompt_template=llm_prompt_template,
#             llm_system_prompt=llm_system_prompt,
#         )
#         manager.commit()
#         return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))
#
#     elif request.method == "POST":
#         logger.error(form.errors)
#
#     storage_instances = manager.storage_instances.get_all()
#     components = ["file_accessor"] if form.is_file else []
#     if source_type.IsMulti:
#         components.append("splitter")
#
#     explanations = EXPLANATION_MAP.get(source_type.Name) or []
#
#     return render_template(
#         "top/edit_source.html",
#         form=form,
#         workflow_id=workflow_id,
#         source_id=source_id,
#         storage_instances=storage_instances,
#         components=components,
#         explanations=explanations,
#         title=f"Edit Source: {source_type.Name}",
#         source=source,
#     )
