from autodoc.workflow import Workflow
from flask_wtf import FlaskForm  # type: ignore
from wtforms import IntegerField  # type: ignore
from wtforms import StringField, SubmitField
from autodoc.db import DatabaseManager
from flask_wtf.file import FileField
from loguru import logger
from wtforms.validators import ValidationError


def create_file_extension_check(extensions: list):
    """Create a validator for a given file extension list."""
    def file_extension_check(_, field):
        file = field.data
        if file:
            filename = file.filename
            # Check if the file extension is allowed
            if not ("." in filename and filename.rsplit(".", 1)[1].lower() in extensions):
                raise ValidationError(f"Invalid file extension. Allowed: {','.join(extensions)}")

    return file_extension_check


def get_form(workflow_id: int, url_params: dict, manager: DatabaseManager):
    """
    Return a dynamic form based on workflow_id.

    If URL params are supplied then the following happens:
     - if the params totally match the fields, then skip the form
     - if some match, then prefill those fields
     - if none match or none given, run the form normally
    """
    print("creating a form based on url params:", url_params)

    field_map = {
        "String": StringField,
        "Integer": IntegerField,
    }

    class Form(FlaskForm):
        submit = SubmitField("Submit")
        upload_file_fields = []
        mapping = {}

    field_data_rst = Workflow.get_form(workflow_id=workflow_id, manager=manager)
    field_data = field_data_rst.data

    field_data_rst.column("FieldName")

    for field in field_data:
        name = field["FieldName"]
        label = field["FieldLabel"] or field["FieldName"]
        field_obj = field_map[field["FieldType"]]

        if url_params and name in url_params.keys():
            setattr(Form, name, field_obj(label, default=url_params.get(name)))

        else:
            setattr(Form, name, field_obj(label))

    # add source uploaded files
    sql = """
        select Source.Id SourceId, SourceType.Name SourceTypeName, Source.Name SourceName
        from Source
        join SourceType
            on Source.TypeId = SourceType.Id
        where SourceType.IsFile = 1
        and source.WorkflowId = :workflow_id
        and source.FileAccessInstanceId is null
    """
    params = {"workflow_id": workflow_id}
    uploaded_files_records = manager.db.recordset(sql, params).data

    upload_file_fields = []  # a list of the filefield names

    file_extension_mapping = {
        "CSVRecord": ["csv"],
        "CSVTable": ["csv"],
        "ExcelRecord": ["xlsx", "xls"],
        "ExcelTable": ["xlsx", "xls"],

    }

    for uploaded_file in uploaded_files_records:
        name = uploaded_file["SourceName"]
        label = f"({uploaded_file['SourceTypeName']}) {uploaded_file['SourceName']}"

        file_extension = file_extension_mapping.get(uploaded_file["SourceTypeName"])
        extension_validator = create_file_extension_check(file_extension)

        setattr(Form, name, FileField(label, validators=[extension_validator]))
        upload_file_fields.append(name)

    # add outcome template uploaded files
    sql = """
        select Outcome.Id, OutcomeType.Name OutcomeTypeName, Outcome.Name OutcomeName
        from Outcome
        join OutcomeType
            on Outcome.OutcomeTypeId = OutcomeType.Id
        where OutcomeType.IsFile = 1
        and Outcome.WorkflowId = :workflow_id
        and outcome.InputFileInstanceId is Null
    """
    params = {"workflow_id": workflow_id}
    outcome_template_uploaded_files_records = manager.db.recordset(sql, params).data

    for uploaded_file in outcome_template_uploaded_files_records:
        name = uploaded_file["OutcomeName"]
        label = f"({uploaded_file['OutcomeTypeName']}) {uploaded_file['OutcomeName']}"
        setattr(Form, name, FileField(label))
        upload_file_fields.append(name)

    if not field_data and not upload_file_fields:
        logger.info("no field dat and no upload file fields.")
        return None

    form = Form()
    form.upload_file_fields = upload_file_fields

    return form
