from flask_wtf import FlaskForm  # type: ignore
from wtforms import IntegerField  # type: ignore
from wtforms import StringField, SubmitField

# from autodoc.db import DatabaseManager
from autodoc.data.manager import DatabaseManager
from flask_wtf.file import FileField
from loguru import logger
from wtforms.validators import ValidationError
from typing import Optional, Any, Dict, List


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


class WorkflowForm(FlaskForm):
    """Define a returnable type class that will be the basis of our dynamic form."""

    upload_file_fields: List[Any]
    mapping: Dict[str, Any]


def get_form(
    workflow_id: int, url_params: dict, manager: DatabaseManager
) -> Optional[WorkflowForm]:
    """
    Return a dynamic form based on workflow_id.

    If URL params are supplied then the following happens:
     - if the params totally match the fields, then skip the form
     - if some match, then prefill those fields
     - if none match or none given, run the form normally

    This is the form that starts an instance of a Workflow.
    """
    field_map = {
        "String": StringField,
        "Integer": IntegerField,
    }
    file_extension_mapping = {
        "CSVRecord": ["csv"],
        "CSVTable": ["csv"],
        "ExcelRecord": ["xlsx", "xls"],
        "ExcelTable": ["xlsx", "xls"],
    }

    class Form(WorkflowForm):
        submit = SubmitField("Submit")
        upload_file_fields = []
        mapping = {}

    # build fields into the Form.
    form_fields = manager.form_fields.get_all(workflow_id=workflow_id)

    for field in form_fields:
        name = field.FieldName
        label = field.FieldLabel or field.FieldName
        field_obj = field_map[field.FieldType]

        if url_params and name in url_params.keys():
            setattr(Form, name, field_obj(label, default=url_params.get(name)))

        else:
            setattr(Form, name, field_obj(label))

    # This holds all upload file field names that have been added to the form to reference later
    upload_file_fields = []

    # build file uploads for sources into the form
    sources_requiring_file_uploads = manager.sources.get_file_uploads(workflow_id=workflow_id)

    for source in sources_requiring_file_uploads:
        name = source.Name
        label = f"({source.source_type.Name}) {source.Name}"

        allowed_file_extensions = file_extension_mapping.get(source.source_type.Name, [])
        extension_validator = create_file_extension_check(allowed_file_extensions)

        setattr(Form, name, FileField(label, validators=[extension_validator]))
        upload_file_fields.append(name)

    # build file uploads for outcomes into the form
    outcomes_requiring_file_upload = manager.outcomes.get_file_uploads(workflow_id=workflow_id)

    for outcome in outcomes_requiring_file_upload:
        name = outcome.Name
        label = f"({outcome.outcome_type.Name}) {outcome.Name}"
        setattr(Form, name, FileField(label))
        upload_file_fields.append(name)

    if not form_fields and not upload_file_fields:
        logger.info("no field data and no upload file fields.")
        return None

    form = Form()
    form.upload_file_fields = upload_file_fields

    return form
