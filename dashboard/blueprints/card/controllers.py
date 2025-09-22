"""Define cards."""

from flask import Blueprint, redirect, render_template, request, url_for
from loguru import logger

from dashboard.database import get_db_manager

card_blueprint = Blueprint("card", "card_blueprint", url_prefix="/card")


@card_blueprint.route("/form_card/<workflow_id>")
def form_card(workflow_id: str):
    """Render a card that shows all form fields."""
    manager = get_db_manager()
    form_fields = manager.form_fields.get_all(workflow_id=workflow_id)
    return render_template(
        "components/cards/sources/form.html",
        form_fields=form_fields,
        workflow_id=workflow_id,
    )


@card_blueprint.route("/source_card/<int:source_id>")
def source_card(source_id: int):
    """Return the source card of a given source id."""
    logger.debug(f"Source Card GET with {source_id=}")
    manager = get_db_manager()
    source = manager.sources.get(source_id=source_id)
    source_type = source.source_type

    if source_type.Name == "CSVRecord":
        return render_template("components/cards/sources/csv_card.html", source=source)

    if source_type.Name == "CSVTable":
        return render_template("components/cards/sources/csv_table_card.html", source=source)

    if source_type.Name == "ExcelRecord":
        return render_template("components/cards/sources/excel_card.html", source=source)

    if source_type.Name == "ExcelTable":
        return render_template("components/cards/sources/excel_table_card.html", source=source)

    if source_type.Name == "SQL Record" and source.database:
        return render_template("components/cards/sources/sql_record_card.html", source=source)

    if source_type.Name == "SQL RecordSet" and source.database:
        return render_template("components/cards/sources/sql_recordset_card.html", source=source)

    if source_type.Name == "SQL RecordSet Transpose" and source.database:
        return render_template(
            "components/cards/sources/sql_recordset_transpose_card.html", source=source
        )

    if source_type.Name == "LLM":
        return render_template(
            "components/cards/sources/llm_card.html", source=source
        )

    raise


@card_blueprint.route("/source_storage_card/<int:source_id>")
def source_storage_card(source_id: int):
    """Return a storage card for file based sources."""
    manager = get_db_manager()
    # source_id = int(request.args.get("source_id"))
    source = manager.sources.get(source_id=source_id)

    if not source.file_template or source.file_template.StorageInstanceId == -1:
        return render_template("components/cards/file_storages/upload.html", name=source.Name)

    file_template = source.file_template
    storage_instance = file_template.storage_instance
    storage_type = storage_instance.storage_type

    if storage_type.Name == "S3":
        url = storage_instance.URL
        bucket = file_template.Bucket
        location = file_template.Location
        return render_template(
            "components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location
        )

    if storage_type.Name == "SharePoint":
        site = storage_instance.URL
        library = storage_instance.RemotePath
        path = file_template.Location
        return render_template(
            "components/cards/file_storages/sharepoint.html", site=site, library=library, path=path
        )

    if storage_type.Name == "Linux Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/linux.html", path=path)

    if storage_type.Name == "Windows Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/windows.html", path=path)

    return render_template("components/cards/file_storages/upload.html", name=source["Name"])


@card_blueprint.route("/sql_text/<int:source_id>")
def sql_text(source_id: int):
    """Return the SQL text of a given source id."""
    # source_id = request.args.get("source_id")
    manager = get_db_manager()
    source = manager.sources.get(source_id=source_id)
    return render_template("components/cards/sql_text.html", source=source)

@card_blueprint.route("/prompt_template/<int:source_id>")
def prompt_template(source_id: int):
    """Return the prompt template of a given source id."""
    # source_id = request.args.get("source_id")
    manager = get_db_manager()
    source = manager.sources.get(source_id=source_id)
    return render_template("components/cards/prompt_text.html", source=source)


@card_blueprint.route("/outcome_card/<int:outcome_id>")
def outcome_card(outcome_id: int):
    """Return the source card of a given source id."""
    logger.info(f"outcome card of id {outcome_id}")
    manager = get_db_manager()
    outcome = manager.outcomes.get(outcome_id=outcome_id)

    if outcome.outcome_type.Name == "HTML":
        return render_template("components/cards/outcomes/html_card.html", outcome=outcome)

    if outcome.outcome_type.Name == "Microsoft Word":
        return render_template("components/cards/outcomes/word_card.html", outcome=outcome)

    if outcome.outcome_type.Name == "PDF":
        return render_template("components/cards/outcomes/pdf_card.html", outcome=outcome)

    raise


@card_blueprint.route("/input_storage_card/<int:outcome_id>")
def outcome_input_storage_card(outcome_id: int):
    """Return a storage card for an outcome for it's input file template."""
    manager = get_db_manager()
    # outcome_id = request.args.get("outcome_id")
    outcome = manager.outcomes.get(outcome_id=outcome_id)

    if not outcome.input_file_template or outcome.input_file_template.StorageInstanceId == -1:
        return render_template("components/cards/file_storages/upload.html", name=outcome.Name)

    file_template = outcome.input_file_template
    storage_instance = file_template.storage_instance
    storage_type = storage_instance.storage_type

    if storage_type.Name == "S3":
        url = storage_instance.URL
        bucket = file_template.Bucket
        location = file_template.Location
        return render_template(
            "components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location
        )

    if storage_type.Name == "SharePoint":
        site = storage_instance.URL
        library = storage_instance.RemotePath
        path = file_template.Location
        return render_template(
            "components/cards/file_storages/sharepoint.html", site=site, library=library, path=path
        )

    if storage_type.Name == "Linux Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/linux.html", path=path)

    if storage_type.Name == "Windows Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/windows.html", path=path)

    return render_template("components/cards/file_storages/upload.html", name=outcome.Name)


@card_blueprint.route("/output_storage_card/<int:outcome_id>")
def outcome_output_storage_card(outcome_id: int):
    """Return a storage card for an outcome for it's input file template."""
    manager = get_db_manager()
    outcome = manager.outcomes.get(outcome_id=outcome_id)

    if not outcome.output_file_template or outcome.output_file_template.StorageInstanceId == -1:
        return render_template(
            "components/cards/file_storages/download.html", name=outcome.DownloadName
        )

    file_template = outcome.output_file_template
    storage_instance = file_template.storage_instance
    storage_type = storage_instance.storage_type

    if storage_type.Name == "S3":
        url = storage_instance.URL
        bucket = file_template.Bucket
        location = file_template.Location
        return render_template(
            "components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location
        )

    if storage_type.Name == "SharePoint":
        site = storage_instance.URL
        library = storage_instance.RemotePath
        path = file_template.Location
        return render_template(
            "components/cards/file_storages/sharepoint.html", site=site, library=library, path=path
        )

    if storage_type.Name == "Linux Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/linux.html", path=path)

    if storage_type.Name == "Windows Share":
        path = storage_instance.RemotePath + file_template.Location
        return render_template("components/cards/file_storages/windows.html", path=path)

    return render_template("components/cards/file_storages/download.html", name=outcome.Name)


@card_blueprint.route("/storage_card/<input_type>")
def outcome_storage_card(input_type: str):
    """Return a storage card for file based outcomes."""
    outcome_id = request.args.get("outcome_id")

    if input_type == "input":
        return redirect(url_for("card.outcome_input_storage_card", outcome_id=outcome_id))
    return redirect(url_for("card.outcome_output_storage_card", outcome_id=outcome_id))
