"""Models for the top level."""

import random
import string

from loguru import logger

from dashboard.database import get_manager


def get_sources(workflow_id):
    """Return all sources for a workflow."""
    return get_manager().get_sources(workflow_id, step=-1).data


def delete_source(source_id):
    """Delete a Source."""
    sql = """
        delete from SourceFormField
        where SourceId = :source_id
    """
    params = {"source_id": source_id}
    manager = get_manager()
    manager.db.execute(sql, params)

    sql = "delete from Source where Id = :source_id"
    manager.db.execute(sql, params)


def delete_outcome(outcome_id):
    """Delete an Outcome."""
    sql = """Delete from Outcome where Id = :outcome_id"""
    params = {"outcome_id": outcome_id}
    get_manager().db.execute(sql, params)


def get_meta_database_choices():
    """Return the list of databases in select field format."""
    manager = get_manager()
    databases = manager.get_meta_databases().data
    database_choices = [(row["DatabaseId"], row["Name"]) for row in databases]
    return database_choices


def get_outcomes(workflow_id):
    """Return all outcomes."""
    manager = get_manager()
    return manager.get_outcomes(workflow_id).data


def create_workflow(name):
    """Create a new workflow."""
    manager = get_manager()
    return manager.create_workflow(name)


def add_record_source(workflow_id: int, sql_text: str, database_id: int, step: int) -> None:
    """Add a record source to the project database."""
    sql = """
        insert into Source
        (WorkflowId, TypeId, DatabaseId, SQLText, Step)
        values
        (:workflow_id, 3, :database_id, :sql_text, :step)
    """
    params = {
        "workflow_id": workflow_id,
        "sql_text": sql_text,
        "database_id": database_id,
        "step": step,
    }
    manager = get_manager()
    manager.db.execute(sql, params=params)


def add_record_set_source(
    workflow_id: int,
    sql_text: str,
    database_id: int,
    field_name: str,
    splitter: bool,
    step: int,
) -> None:
    """Add a record set source to the project database."""
    sql = """
        insert into Source
        (WorkflowId, TypeId, DatabaseId, SQLText, FieldName, Splitter, Step)
        values
        (:workflow_id, 5, :database_id, :sql_text, :field_name, :splitter, :step)
    """
    params = {
        "workflow_id": workflow_id,
        "sql_text": sql_text,
        "database_id": database_id,
        "field_name": field_name if not splitter else None,
        "splitter": splitter,
        "step": step,
    }
    logger.info(params)
    manager = get_manager()
    manager.db.execute(sql, params=params)


def add_csv_table_source(
    workflow_id: int,
    field_name: str,
    splitter: bool,
    step: int,
    location: str | None = None,
    bucket: str | None = None,
    file_access_id: int | None = None,
    name: str | None = None,
) -> None:
    """Add a csv table source to the project database."""
    manager = get_manager()
    file_instance_id = None

    sql = "select Id from SourceType where Name = 'CSVTable'"
    source_type_id = manager.db.record_scalar(sql).sdatum()

    if file_access_id:
        file_instance_id = manager.add_file_access_instance(
            file_access_id=file_access_id,
            location=location,
            bucket=bucket,
        )

    manager = get_manager()
    sql = "select Id from SourceType where Name = 'CSVTable'"
    source_type_id = manager.db.record_scalar(sql).sdatum()

    sql = """
        insert into Source
        (WorkflowId, TypeId,FieldName, Splitter, Step, FileAccessInstanceId, Name)
        values
        (:workflow_id, :source_type_id, :field_name, :splitter, :step, :file_instance_id, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "source_type_id": source_type_id,
        "field_name": field_name,
        "splitter": splitter,
        "step": step,
        "file_instance_id": file_instance_id,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_record_set_transpose_source(
    workflow_id: int,
    sql_text: str,
    database_id: int,
    key_field: str,
    value_field: str,
    step: int,
) -> None:
    """Add a record set source to the project database."""
    manager = get_manager()
    manager.add_source(
        workflow_id=workflow_id,
        type_id=6,
        sql_text=sql_text,
        database_id=database_id,
        key_field=key_field,
        value_field=value_field,
        step=step,
    )


def get_source(source_id):
    """Get all details for a source."""
    sql = """
        select
            Source.Id SourceId,
            WorkflowId,
            TypeId,
            SourceType.Name,
            SourceType.IsSlow,
            Location,
            ZIndex,
            SQLSourceId,
            SQLText,
            SQLConnectionName,
            SourceFormField.FieldType FormFieldType,
            SourceFormField.FieldName FormFieldName
        from Source
        join SourceType
            on Source.TypeId = SourceType.Id
        left join SourceFormField
            on SourceFormField.SourceId = Source.Id
        where Source.Id = :source_id
    """
    params = {"source_id": source_id}
    manager = get_manager()
    return manager.db.record(sql, params=params).data


def get_form_fields(workflow_id):
    """Get a list of records of form fields for a given workflow id."""
    sql = """
        select
            SourceFormField.Id FormFieldId,
            SourceFormField.FieldType FieldType,
            SourceFormField.FieldName FieldName,
            SourceFormField.FieldLabel FieldLabel
        from Source
        inner join SourceType
            on Source.TypeId = SourceType.Id
        left join SourceFormField
            on SourceFormField.SourceId = Source.Id
        where Source.WorkflowId = :workflow_id
        and SourceType.Name = 'Form'
    """
    params = {"workflow_id": workflow_id}
    manager = get_manager()
    return manager.db.recordset(sql, params=params).data


def get_form_fields_from_source(source_id):
    """Get a list of records of form fields for a given source id."""
    sql = """
        select
            SourceFormField.FieldType FieldType,
            SourceFormField.FieldName FieldName,
            SourceFormField.FieldLabel FieldLabel
        from Source
        left join SourceFormField
            on SourceFormField.SourceId = Source.Id
        where Source.Id = :source_id
    """
    params = {"source_id": source_id}
    manager = get_manager()
    return manager.db.recordset(sql, params=params).data


def run_on_form_stage(run_id):
    """Return if the run of run_id is currently stopped on a form source."""
    return True


def add_csv_record_source(
    workflow_id: int,
    orientation: str,
    step: int,
    location: str | None = None,
    bucket: str | None = None,
    file_access_id: int | None = None,
    name: str | None = None,
) -> None:
    """Add a csv record source to the project database."""
    manager = get_manager()
    file_instance_id = None

    sql = "select Id from SourceType where Name = 'CSVRecord'"
    source_type_id = manager.db.record_scalar(sql).sdatum()

    if file_access_id:
        file_instance_id = manager.add_file_access_instance(
            file_access_id=file_access_id,
            location=location,
            bucket=bucket,
        )

    sql = """
        insert into Source
        (WorkflowId, TypeId, Step, Orientation, FileAccessInstanceId, Name)
        values
        (:workflow_id, :source_type_id, :step, :orientation, :file_instance_id, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "source_type_id": source_type_id,
        "step": step,
        "orientation": orientation,
        "file_instance_id": file_instance_id,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_html_outcome(
    workflow_id,
    input_file_access_id,
    input_location,
    input_bucket,
    output_file_access_id,
    output_location,
    output_bucket,
    name,
):
    """Add a HTML outcome."""
    manager = get_manager()
    input_file_instance_id = None
    output_file_instance_id = None

    if input_file_access_id:
        input_file_instance_id = manager.add_file_access_instance(
            file_access_id=input_file_access_id,
            location=input_location,
            bucket=input_bucket,
        )

    if output_file_access_id:
        output_file_instance_id = manager.add_file_access_instance(
            file_access_id=output_file_access_id,
            location=output_location,
            bucket=output_bucket,
        )

    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, InputFileInstanceId, OutputFileInstanceId, Name)
        values
        (:workflow_id, 1, :input_file_instance_id, :output_file_instance_id, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "input_file_instance_id": input_file_instance_id,
        "output_file_instance_id": output_file_instance_id,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_word_outcome(
    workflow_id,
    input_file_access_id,
    input_location,
    input_bucket,
    output_file_access_id,
    output_location,
    output_bucket,
    name,
) -> None:
    """Add Microsoft Word Outcome to the database."""
    manager = get_manager()
    input_file_instance_id = None
    output_file_instance_id = None

    if input_file_access_id:
        input_file_instance_id = manager.add_file_access_instance(
            file_access_id=input_file_access_id,
            location=input_location,
            bucket=input_bucket,
        )

    if output_file_access_id:
        output_file_instance_id = manager.add_file_access_instance(
            file_access_id=output_file_access_id,
            location=output_location,
            bucket=output_bucket,
        )

    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, InputFileInstanceId, OutputFileInstanceId, Name)
        values
        (:workflow_id, 2, :input_file_instance_id, :output_file_instance_id, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "input_file_instance_id": input_file_instance_id,
        "output_file_instance_id": output_file_instance_id,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_pdf_outcome(
    workflow_id,
    input_file_access_id,
    input_location,
    input_bucket,
    output_file_access_id,
    output_location,
    output_bucket,
    name,
) -> None:
    """Add PDF Outcome to the database."""
    manager = get_manager()
    input_file_instance_id = None
    output_file_instance_id = None

    if input_file_access_id:
        input_file_instance_id = manager.add_file_access_instance(
            file_access_id=input_file_access_id,
            location=input_location,
            bucket=input_bucket,
        )

    if output_file_access_id:
        output_file_instance_id = manager.add_file_access_instance(
            file_access_id=output_file_access_id,
            location=output_location,
            bucket=output_bucket,
        )

    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, InputFileInstanceId, OutputFileInstanceId, Name)
        values
        (:workflow_id, 3, :input_file_instance_id, :output_file_instance_id, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "input_file_instance_id": input_file_instance_id,
        "output_file_instance_id": output_file_instance_id,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_word_combination_outcome(workflow_id: int, output_location: str, name: str) -> None:
    """Add a Microsoft Word Combination Document outcome to the project database."""
    print("adding word combination outcome")
    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, OutputLocation, Name)
        values
        (:workflow_id, 4, :output_location, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "output_location": output_location,
        "name": name,
    }
    manager = get_manager()
    manager.db.execute(sql, params=params)


def add_pdf_combination_outcome(workflow_id: int, output_location: str, name: str) -> None:
    """Add a PDF Combination Document outcome to the project database."""
    manager = get_manager()
    sql = "select Id From OutcomeType where Name = 'PDF Combination'"
    outcome_type_id = manager.db.record_scalar(sql).sdatum()

    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, OutputLocation, Name)
        values
        (:workflow_id, :outcome_type_id, :output_location, :name)
    """
    params = {
        "workflow_id": workflow_id,
        "outcome_type_id": outcome_type_id,
        "output_location": output_location,
        "name": name,
    }
    manager.db.execute(sql, params=params)


def add_form_field_source(workflow_id, name, label, field_type):
    manager = get_manager()
    sql = """
        select Id
        from Source
        where WorkflowId = :workflow_id
        and TypeId = 4
    """
    params = {"workflow_id": workflow_id}
    source_id = manager.db.record_scalar(sql, params=params).sdatum()

    if not source_id:
        # no form source exists yet
        sql = """
            insert into Source
            (WorkflowId, TypeId)
            values
            (:workflow_id, 4)
        """
        manager.db.execute(sql, params=params)

        sql = """
            select Id
            from Source
            where WorkflowId = :workflow_id
            and TypeId = 4
        """
        source_id = manager.db.record_scalar(sql, params=params).sdatum()

    sql = """
        insert into SourceFormField
        (SourceId, FieldType, FieldName, FieldLabel)
        values
        (:source_id, :field_type, :name, :label)
    """
    params = {
        "source_id": source_id,
        "field_type": field_type,
        "name": name,
        "label": label,
    }
    manager.db.execute(sql, params=params)


def add_sql_field_to_source(source_id, field):
    """Add a sql field to source."""
    manager = get_manager()
    sql = """
        insert into SQLFields
        (SourceId, FieldName)
        values
        (:source_id, :field)
    """
    params = {"source_id": source_id, "field": field}
    manager.db.execute(sql, params=params)


def get_workflow_name(workflow_id):
    """Get workflow name."""
    manager = get_manager()
    sql = """select Name from Workflow where Id = :workflow_id"""
    params = {"workflow_id": workflow_id}
    return manager.db.record_scalar(sql, params=params).sdatum()


def generate_random_filename(extension: str, length: int = 10) -> str:
    """
    Return a random but unique filename with a given extension.

    example with extension = "docx" and length = 10
    > alfkeospwl.docx
    """
    letters = string.ascii_lowercase
    stem = "".join(random.choice(letters) for _ in range(length))

    filename = f"{stem}.{extension.replace('.', '')}"
    return filename


def get_word_combination_choices(workflow_id: int) -> list:
    """Get a list of word combination options from the database."""
    manager = get_manager()
    sql = """
        select a.Id, a.Name
        from Outcome a
        join OutcomeType b
            on a.OutcomeTypeId = b.Id
        where a.WorkflowId = :workflow_id
        and (
            b.Name = 'Word Combination'
            or b.Name = 'PDF Combination')
    """
    params = {"workflow_id": workflow_id}
    return manager.db.recordset(sql, params=params).data


def add_word_subdocument_outcome(
    workflow_id: int,
    input_location: str,
    file_upload: bool,
    parent_outcome_id: int,
    document_order: int,
    filter_field: str | None,
    filter_value: str | None,
) -> None:
    """Add a Microsoft Word SubDocument outcome to the project database."""
    manager = get_manager()
    sql = """
        insert into Outcome
        (WorkflowId, OutcomeTypeId, InputLocation, FileUpload, ParentOutcomeId, DocumentOrder,
            FilterField, FilterValue)
        values
        (:workflow_id, 5, :input_location, :file_upload, :parent_outcome_id, :document_order,
            :filter_field, :filter_value)
    """
    params = {
        "workflow_id": workflow_id,
        "input_location": input_location,
        "file_upload": file_upload,
        "parent_outcome_id": parent_outcome_id,
        "document_order": document_order,
        "filter_field": filter_field,
        "filter_value": filter_value,
    }
    manager.db.execute(sql, params=params)


def get_instances(workflow_id: int) -> list:
    """Get a list of instances."""
    manager = get_manager()
    sql = """
        select InstanceId, StartTime
        from WorkflowInstance
        where WorkflowId = :workflow_id
        order by InstanceId desc
        limit 5
    """
    params = {"workflow_id": workflow_id}
    return manager.db.recordset(sql, params=params).data


def get_instance(instance_id: int) -> dict:
    """Return information about an instance."""
    manager = get_manager()
    sql = """
        select WorkflowInstance.InstanceId, WorkflowId, StartTime, Workflow.Name
        from WorkflowInstance
        join Workflow
            on WorkflowInstance.WorkflowId = Workflow.Id
        where WorkflowInstance.InstanceId = :instance_id
    """
    params = {"instance_id": instance_id}
    return manager.db.record(sql, params=params).data


def get_instance_source_events(instance_id: int) -> list:
    """Return a list of source events for an instance."""
    manager = get_manager()
    sql = """
        select a.SourceId, SourceData, SourceDataOngoing, st.Name SourceType
        from WorkflowInstanceEvent a
        join Source s
            on a.SourceId = s.Id
        join SourceType st
            on s.TypeId = st.Id
        where a.OutcomeId is null
        and a.WorkflowInstanceId = :instance_id
    """
    params = {"instance_id": instance_id}
    return manager.db.recordset(sql, params=params).data


def get_instance_outcome_events(instance_id: int) -> list:
    """Return a list of outcome events for an instance."""
    sql = """
        select a.OutcomeId, ot.Name OutcomeType, a.OutcomeLocation
        from WorkflowInstanceEvent a
        join Outcome o
            on a.OutcomeId = o.Id
        join OutcomeType ot
            on o.OutcomeTypeId = ot.Id
        where a.OutcomeId is not null
        and a.WorkflowInstanceId = :instance_id
    """
    params = {"instance_id": instance_id}
    manager = get_manager()
    return manager.db.recordset(sql, params=params).data


def add_access_record_source(
    workflow_id: int,
    location: str | None,
    sql_text: str,
    step: int,
) -> None:
    """Add a access record source to the project database."""
    sql = "select Id from SourceType where Name = 'AccessRecord'"
    manager = get_manager()
    source_type_id = manager.db.record_scalar(sql).sdatum()

    sql = """
        insert into Source
        (WorkflowId, TypeId, Location, SQLText, Step)
        values
        (:workflow_id, :source_type_id, :location, :sql, :step)
    """
    params = {
        "workflow_id": workflow_id,
        "source_type_id": source_type_id,
        "location": location,
        "sql": sql_text,
        "step": step,
    }
    manager.db.execute(sql, params=params)


def add_access_record_set_source(
    workflow_id: int,
    sql_text: str,
    location: str,
    field_name: str,
    splitter: bool,
    step: int,
) -> None:
    """Add an access record set source to the project database."""
    sql = "select Id from SourceType where Name = 'AccessRecordSet'"
    manager = get_manager()
    source_type_id = manager.db.record_scalar(sql).sdatum()

    sql = """
        insert into Source
        (WorkflowId, TypeId, SQLText, Location, FieldName, Splitter, Step)
        values
        (:workflow_id, :source_type_id, :sql_text, :location, :field_name, :splitter, :step)
    """
    params = {
        "workflow_id": workflow_id,
        "source_type_id": source_type_id,
        "sql_text": sql_text,
        "location": location,
        "field_name": field_name if not splitter else None,
        "splitter": splitter,
        "step": step,
    }
    manager.db.execute(sql, params=params)


def get_file_accessors():
    """Get a current list of file accessors to be inserted into an add source page."""
    manager = get_manager()
    sql = "select * from vFileAccessors"
    return manager.db.recordset(sql).data


def delete_form_field(form_field_id: int):
    """Delete a form field."""
    sql = """
        delete from SourceFormField
        where Id = :form_field_id
    """
    params = {"form_field_id": form_field_id}
    manager = get_manager()
    manager.db.execute(sql, params)
