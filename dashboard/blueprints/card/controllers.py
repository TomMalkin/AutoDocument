"""Define cards."""

from flask import Blueprint, render_template, request
from dashboard.database import get_manager
from loguru import logger

card_blueprint = Blueprint("card", "card_blueprint", url_prefix="/card")


@card_blueprint.route("/form_card/<workflow_id>")
def form_card(workflow_id: str):
    """Render a card that shows all form fields."""
    sql = """
        select
            SourceFormField.FieldType Type,
            SourceFormField.FieldName Name,
            SourceFormField.FieldLabel Label,
            SourceFormField.Id FormFieldId
        from Source
        join SourceFormField
            on Source.Id = SourceFormField.SourceId
        where Source.WorkflowId = :workflow_id
    """
    params = {"workflow_id": workflow_id}
    form_records = get_manager().db.recordset(sql=sql, params=params).data
    return render_template(
        "components/cards/sources/form.html",
        form_records=form_records,
        workflow_id=workflow_id,
    )


@card_blueprint.route("/source_card/<source_id>")
def source_card(source_id: str):
    """Return the source card of a given source id."""
    logger.debug(f"Source Card GET with {source_id=}")
    manager = get_manager()
    sql = " select * from vSource where SourceId = :source_id and TypeName != 'Form'"
    params = {"source_id": int(source_id)}
    source_record = manager.db.record(sql=sql, params=params).data

    if source_record["TypeName"] == "CSVRecord":
        orientation = source_record["Orientation"]
        return render_template(
            "components/cards/sources/csv_card.html",
            source_id=int(source_id),
            orientation=orientation,
            workflow_id=source_record["WorkflowId"],
        )

    if source_record["TypeName"] == "CSVTable":
        return render_template(
            "components/cards/sources/csv_table_card.html",
            multi_type="Splitter" if source_record["Splitter"] else "Field",
            source_id=int(source_id),
            field_name=source_record["FieldName"],
            workflow_id=source_record["WorkflowId"],
        )

    if source_record["TypeName"] == "ExcelRecord":
        return render_template(
            "components/cards/sources/excel_card.html",
            source_id=int(source_id),
            workflow_id=source_record["WorkflowId"],
            sheet_name=source_record["SheetName"],
            header_row=source_record["HeaderRow"],
        )

    if source_record["TypeName"] == "ExcelTable":
        return render_template(
            "components/cards/sources/excel_table_card.html",
            multi_type="Splitter" if source_record["Splitter"] else "Field",
            source_id=int(source_id),
            field_name=source_record["FieldName"],
            workflow_id=source_record["WorkflowId"],
            sheet_name=source_record["SheetName"],
            header_row=source_record["HeaderRow"],
        )

    if source_record["TypeName"] == "SQL Record":
        database_name = source_record["DatabaseName"]
        return render_template(
            "components/cards/sources/sql_record_card.html",
            source_id=int(source_id),
            database_name=database_name,
            workflow_id=source_record["WorkflowId"],
        )

    if source_record["TypeName"] == "SQL RecordSet":
        database_name = source_record["DatabaseName"]
        return render_template(
            "components/cards/sources/sql_recordset_card.html",
            multi_type="Splitter" if source_record["Splitter"] else "Field",
            source_id=int(source_id),
            field_name=source_record["FieldName"],
            database_name=database_name,
            workflow_id=source_record["WorkflowId"],
        )

    if source_record["TypeName"] == "SQL RecordSet Transpose":
        database_name = source_record["DatabaseName"]
        key_field = source_record["KeyField"]
        value_field = source_record["ValueField"]
        return render_template(
            "components/cards/sources/sql_recordset_transpose_card.html",
            source_id=int(source_id),
            database_name=database_name,
            key_field=key_field,
            value_field=value_field,
            workflow_id=source_record["WorkflowId"],
        )


@card_blueprint.route("/source_storage_card")
def source_storage_card():
    """Return a storage card for file based sources."""
    manager = get_manager()
    source_id = request.args.get("source_id")
    sql = "select * from vSource where SourceId = :source_id"
    params = {"source_id": source_id}
    record = manager.db.record(sql=sql, params=params).data

    if record["FileAccessTypeName"] == "S3":
        url = record["URL"]
        bucket = record["Bucket"]
        location = record["Location"]
        return render_template(
            "components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location
        )

    if record["FileAccessTypeName"] == "SharePoint":
        site = record["URL"]
        library = record["RemotePath"]
        path = record["Location"]
        return render_template(
            "components/cards/file_storages/sharepoint.html", site=site, library=library, path=path
        )

    if record["FileAccessTypeName"] == "Linux Share":
        path = record["RemotePath"] + record["Location"]
        return render_template("components/cards/file_storages/linux.html", path=path)

    if record["FileAccessTypeName"] == "Windows Share":
        path = record["RemotePath"] + record["Location"]
        return render_template("components/cards/file_storages/windows.html", path=path)

    return render_template("components/cards/file_storages/upload.html")


@card_blueprint.route("/sql_text")
def sql_text():
    """Return the SQL text of a given source id."""
    source_id = request.args.get("source_id")
    sql = "select SQLText from Source where ID = :source_id"
    params = {"source_id": source_id}
    text = get_manager().db.record(sql=sql, params=params).data["SQLText"]
    return render_template("components/cards/sql_text.html", text=text)


@card_blueprint.route("/outcome_card/<outcome_id>")
def outcome_card(outcome_id: str):
    """Return the source card of a given source id."""
    logger.info(f"outcome card of id {outcome_id}")
    manager = get_manager()
    sql = " select * from vOutcome where OutcomeId = :outcome_id"
    params = {"outcome_id": int(outcome_id)}
    outcome_record = manager.db.record(sql=sql, params=params).data
    workflow_id = outcome_record["WorkflowId"]

    if outcome_record["OutcomeTypeName"] == "HTML":
        return render_template(
            "components/cards/outcomes/html_card.html",
            outcome_id=int(outcome_id),
            workflow_id=workflow_id,
        )

    if outcome_record["OutcomeTypeName"] == "Microsoft Word":
        return render_template(
            "components/cards/outcomes/word_card.html",
            outcome_id=int(outcome_id),
            workflow_id=workflow_id,
        )

    if outcome_record["OutcomeTypeName"] == "PDF":
        return render_template(
            "components/cards/outcomes/pdf_card.html",
            outcome_id=int(outcome_id),
            workflow_id=workflow_id,
        )


@card_blueprint.route("/storage_card/<input_type>")
def outcome_storage_card(input_type: str):
    """Return a storage card for file based outcomes."""
    manager = get_manager()
    outcome_id = request.args.get("outcome_id")
    sql = "select * from vOutcome where OutcomeId = :outcome_id"
    params = {"outcome_id": outcome_id}
    record = manager.db.record(sql=sql, params=params).data

    column = "InputFileTypeName" if input_type == "input" else "OutputFileTypeName"
    remote_column = "InputRemotePath" if input_type == "input" else "OutputRemotePath"
    location_column = "InputFileLocation" if input_type == "input" else "OutputFileLocation"
    url_column = "InputURL" if input_type == "input" else "OutputURL"
    bucket_column = "InputFileBucket" if input_type == "input" else "OutputFileBucket"

    if record[column] == "S3":
        url = record[url_column]
        bucket = record[bucket_column]
        location = record[location_column]
        return render_template(
            "components/cards/file_storages/s3.html", url=url, bucket=bucket, location=location
        )

    if record[column] == "SharePoint":
        site = record[url_column]
        library = record[remote_column]
        path = record[remote_column]
        return render_template(
            "components/cards/file_storages/sharepoint.html", site=site, library=library, path=path
        )

    if record[column] == "Linux Share":
        path = record[remote_column] + record[location_column]
        return render_template("components/cards/file_storages/linux.html", path=path)

    if record[column] == "Windows Share":
        path = record[remote_column] + record[location_column]
        return render_template("components/cards/file_storages/windows.html", path=path)

    if input_type == "output":
        return render_template("components/cards/file_storages/download.html")

    return render_template("components/cards/file_storages/upload.html")
