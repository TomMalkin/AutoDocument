"""Define the repositories."""

import datetime
from typing import Optional

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from .tables import (
    DatabaseMetaSource,
    FileTemplate,
    FormField,
    Outcome,
    OutcomeType,
    Source,
    SourceType,
    StorageInstance,
    StorageType,
    Workflow,
    WorkflowInstance,
)

from loguru import logger


class Repository:
    """Base class Repository with generic init."""

    def __init__(self, session: Session):
        """Create a new repository instance based on a session."""
        self.session = session


class SQLFieldsRepository(Repository):
    """Repository for the SQLFields Table."""


class FormFieldRepository(Repository):
    """Repository for the FormField Table."""

    def get_all(self, workflow_id) -> list[FormField]:
        """Get all form fields for a given workflow."""
        stmt = select(FormField).where(FormField.WorkflowId == workflow_id)
        return self.session.scalars(stmt).all()

    def delete(self, form_field_id: int):
        """Delete a form field."""
        stmt = delete(FormField).where(FormField.Id == form_field_id)
        self.session.execute(stmt)

    def form_exists(self, workflow_id: int) -> bool:
        """Return if form fields exist for a given Workflow."""
        stmt = select(FormField).where(FormField.WorkflowId == workflow_id)
        return bool(self.session.scalars(stmt).first())

    def add(self, workflow_id: int, name: str, label: str, field_type: str) -> FormField:
        """Add a form field to a Workflow."""
        form_field = FormField(
            WorkflowId=workflow_id, FieldType=field_type, FieldName=name, FieldLabel=label
        )
        self.session.add(form_field)
        self.session.flush()
        return form_field


class WorkflowRepository(Repository):
    """The repository of actions on the Workflow Table."""

    def get(self, workflow_id: int) -> Workflow:
        """Get a Workflow from an Id."""
        return self.session.get(Workflow, workflow_id)

    def get_all(self) -> list[Workflow]:
        """Get all workflows."""
        stmt = select(Workflow)
        return self.session.scalars(stmt).all()

    def add(self, name: str) -> Workflow:
        """Add a Workflow to the table and return."""
        workflow = Workflow(Name=name)
        self.session.add(workflow)
        self.session.flush()
        return workflow

    def delete(self, workflow_id: int):
        """Delete a Workflow."""
        stmt = delete(Workflow).where(Workflow.Id == workflow_id)
        self.session.execute(stmt)


class WorkflowInstanceRepository(Repository):
    """The repository of actions on the WorkflowInstance Table."""

    def get_all(self, workflow_id: int) -> list[WorkflowInstance]:
        """Get all instances of a workflow."""
        stmt = select(WorkflowInstance).where(WorkflowInstance.WorkflowId == workflow_id)
        return self.session.scalars(stmt).all()

    def add(self, workflow_id: int, step: int) -> WorkflowInstance:
        """Add a new workflow instance."""
        instance = WorkflowInstance(
            ParentInstanceId=None,
            WorkflowId=workflow_id,
            StartTime=datetime.datetime.now().timestamp(),
            EndTime=None,
            Completed=False,
            Data="",
            Step=step,
        )
        self.session.add(instance)
        self.session.flush()
        return instance

    def add_split(
        self, parent_instance_id: int, start_time: datetime.datetime, step: int
    ) -> WorkflowInstance:
        """Add a new instance based on the splitting of another Workflow."""
        instance = WorkflowInstance(
            ParentInstanceId=parent_instance_id,
            StartTime=datetime.datetime.now().timestamp(),
            Step=step,
        )
        self.session.add(instance)
        self.session.flush()
        return instance


class DatabaseMetaSourceRepository(Repository):
    """The repository of actions on the DatabaseMetaSource Table."""

    def get_all(self) -> list[DatabaseMetaSource]:
        """Get all user defined databases."""
        stmt = select(DatabaseMetaSource)
        return self.session.scalars(stmt).all()

    def delete(self, database_id: int):
        """Delete a database meta source."""
        stmt = delete(DatabaseMetaSource).where(DatabaseMetaSource.DatabaseId == database_id)
        self.session.execute(stmt)

    def add(self, name: str, connection_string: str) -> DatabaseMetaSource:
        """Add a database meta source."""
        database = DatabaseMetaSource(Name=name, ConnectionString=connection_string)
        self.session.add(database)
        self.session.flush()
        return database


class OutcomeTypeRepository(Repository):
    """The repository of actions on the OutcomeType Table."""

    def get_from_name(self, name: str) -> OutcomeType:
        """Get the Outcome Id from a name."""
        stmt = select(OutcomeType).where(OutcomeType.Name == name)
        outcome_type = self.session.scalars(stmt).first()
        return outcome_type

    def seed(self):
        """Ensure type tables include up to date types."""
        outcome_types_required = [
            OutcomeType(Name="HTML", IsFile=1),
            OutcomeType(Name="Microsoft Word", IsFile=1),
            OutcomeType(Name="PDF", IsFile=1),
        ]
        outcome_types_to_add = []

        existing_types = set(self.session.scalars(select(OutcomeType.Name)))

        for outcome_type in outcome_types_required:
            if outcome_type.Name not in existing_types:
                outcome_types_to_add.append(outcome_type)

        if outcome_types_to_add:
            self.session.add_all(outcome_types_to_add)

        else:
            logger.info(f"{outcome_types_to_add=}")


class SourceTypeRepository(Repository):
    """The repository of actions on the SourceType Table."""

    def get_from_name(self, name: str) -> SourceType:
        """Get the source Id from a name."""
        stmt = select(SourceType).where(SourceType.Name == name)
        source_type = self.session.scalars(stmt).first()
        return source_type

    def seed(self):
        """Ensure type tables include up to date types."""
        source_types_required = [
            SourceType(Name="YAML", IsSlow=0, IsFile=1, IsMulti=0),
            SourceType(Name="RecordScalar", IsSlow=0, IsFile=0, IsMulti=0),
            SourceType(Name="SQL Record", IsSlow=0, IsFile=0, IsMulti=0),
            SourceType(Name="SQL RecordSet", IsSlow=0, IsFile=0, IsMulti=1),
            SourceType(Name="SQL RecordSet Transpose", IsSlow=0, IsFile=1, IsMulti=0),
            SourceType(Name="CSVRecord", IsSlow=0, IsFile=1, IsMulti=0),
            SourceType(Name="CSVTable", IsSlow=0, IsFile=1, IsMulti=1),
            SourceType(Name="ExcelRecord", IsSlow=0, IsFile=1, IsMulti=0),
            SourceType(Name="ExcelTable", IsSlow=0, IsFile=1, IsMulti=1),
        ]
        source_types_to_add = []

        existing_types = set(self.session.scalars(select(SourceType.Name)))

        for source_type in source_types_required:
            if source_type.Name not in existing_types:
                source_types_to_add.append(source_type)

        if source_types_to_add:
            self.session.add_all(source_types_to_add)


class StorageTypeRepository(Repository):
    """The repository of actions on the StorageType Table."""

    def get_by_name(self, name: str) -> StorageType:
        """Get a StorageType based on it's name."""
        stmt = select(StorageType).where(StorageType.Name == name)
        return self.session.scalars(stmt).first()

    def seed(self):
        """Ensure type tables include up to date types."""
        storage_types_required = [
            StorageType(Name="Download"),
            StorageType(Name="Windows Share"),
            StorageType(Name="Linux Share"),
            StorageType(Name="S3"),
            StorageType(Name="SharePoint"),
        ]
        storage_types_to_add = []

        existing_types = set(self.session.scalars(select(StorageType.Name)))

        for storage_type in storage_types_required:
            if storage_type.Name not in existing_types:
                storage_types_to_add.append(storage_type)

        if storage_types_to_add:
            self.session.add_all(storage_types_to_add)


class StorageInstanceRepository(Repository):
    """The repository of actions on the StorageInstance Table."""

    def get(self, storage_instance_id: int) -> StorageInstance:
        """Get a StorageInstance from an Id."""
        return self.session.get(StorageInstance, storage_instance_id)

    def get_all_of_type(self, storage_type: str) -> list[StorageInstance]:
        """Get all Storage Instances of a given type."""
        stmt = select(StorageInstance).join(StorageType).where(StorageType.Name == storage_type)
        return self.session.scalars(stmt).all()

    def get_all(self) -> list[StorageInstance]:
        """Get all Storage Instances that aren't the Download special type."""
        stmt = select(StorageInstance).join(StorageType).where(StorageType.Name != "Download")
        return self.session.scalars(stmt).all()

    def delete(self, storage_instance_id: int):
        """Delete a StorageInstance."""
        stmt = delete(StorageInstance).where(StorageInstance.Id == storage_instance_id)
        self.session.execute(stmt)

    def add(
        self,
        storage_type: StorageType,
        local_path: Optional[str] = None,
        remote_path: Optional[str] = None,
        top_level: Optional[str] = None,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[StorageInstance]:
        """Add a new storage instance."""
        storage_instance = StorageInstance(
            StorageTypeId=storage_type.Id,
            LocalPath=local_path,
            RemotePath=remote_path,
            TopLevel=top_level,
            URL=url,
            Username=username,
            Password=password,
        )
        self.session.add(storage_instance)
        self.session.flush()
        return storage_instance


class FileTemplateRepository(Repository):
    """The repository of actions on the FileTemplate Table."""

    def get_optional(
        self, storage_instance_id: Optional[int], location: Optional[str], bucket: Optional[str]
    ) -> Optional[int]:
        """
        Return a file access Id that can be used to link a source or outcome.

        It is optional because if uploading or downloading, then the returned Id should be None.
        """
        if not storage_instance_id or storage_instance_id == -1:
            return None

        return self.add(storage_instance_id=storage_instance_id, location=location, bucket=bucket)

    def add(
        self, storage_instance_id: int, location: Optional[str], bucket: Optional[str]
    ) -> FileTemplate:
        """Add a new fila access isntance."""
        file_template = FileTemplate(
            StorageInstanceId=storage_instance_id, Location=location, Bucket=bucket
        )
        self.session.add(file_template)
        self.session.flush()
        return file_template


class OutcomeRepository(Repository):
    """Repository for the Outcomes Table."""

    def get(self, outcome_id: int) -> Outcome:
        """Get an outcome and it's type from an outcome Id."""
        return self.session.get(Outcome, outcome_id)

    def get_file_uploads(self, workflow_id: int) -> list[Outcome]:
        """Get Outcomes that require a template to be uploaded when the Workflow is processed."""
        stmt = (
            select(Outcome)
            .join(OutcomeType)
            .join(FileTemplate, Outcome.OutputFileTemplateId == FileTemplate.Id, isouter=True)
            .where(OutcomeType.IsFile)
            .where(Outcome.WorkflowId == workflow_id)
            .where(or_(Outcome.InputFileTemplateId.is_(None), FileTemplate.StorageInstanceId == -1))
        )
        return self.session.scalars(stmt).all()

    def delete(self, outcome_id: int):
        """Delete an outcome."""
        stmt = delete(Outcome).where(Outcome.Id == outcome_id)
        self.session.execute(stmt)

    def get_all(self, workflow_id: int) -> list[Outcome]:
        """Get all outcomes for a given workflow."""
        stmt = select(Outcome).where(Outcome.WorkflowId == workflow_id)
        return self.session.scalars(stmt).all()

    def add(
        self,
        workflow_id: int,
        outcome_type: OutcomeType,
        name: Optional[str],
        input_instance_id: Optional[int],
        output_instance_id: Optional[int],
        file_upload: bool = False,
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
        download_name: Optional[str] = None,
    ) -> Outcome:
        """Add a new Outcome."""
        outcome = Outcome(
            WorkflowId=workflow_id,
            OutcomeTypeId=outcome_type.Id,
            FileUpload=file_upload,
            FilterField=filter_field,
            FilterValue=filter_value,
            Name=name,
            InputFileTemplateId=input_instance_id,
            OutputFileTemplateId=output_instance_id,
            DownloadName=download_name,
        )
        self.session.add(outcome)
        self.session.flush()
        return outcome


class SourceRepository(Repository):
    """Repository for the Source Table."""

    def get(self, source_id: int) -> Source:
        """Get a single Source."""
        return self.session.get(Source, source_id)

    def get_file_uploads(self, workflow_id: int) -> list[Source]:
        """
        Get Sources that require a file upload for a given Workflow.

        In order to require an upload, the source must have a type that is marked
        as IsFile = 1, and also have a null value for FileTemplateId.
        """
        stmt = (
            select(Source)
            .join(SourceType)
            .join(FileTemplate, isouter=True)
            .where(SourceType.IsFile)
            .where(or_(Source.FileTemplateId.is_(None), FileTemplate.StorageInstanceId == -1))
            .where(Source.WorkflowId == workflow_id)
        )
        return self.session.scalars(stmt).all()

    def get_all(self, workflow_id: int) -> list[Source]:
        """Get all sources for a Workflow."""
        stmt = select(Source).where(Source.WorkflowId == workflow_id)
        return self.session.scalars(stmt).all()

    def get_all_from_step(self, workflow_id: int, step: int) -> list[Source]:
        """Get all sources for a Workflow for a given step onwards."""
        stmt = (
            select(Source)
            .where(Source.WorkflowId == workflow_id)
            .where(Source.Step >= step)
            .order_by(Source.Step.asc(), Source.Splitter.asc())
        )
        return self.session.scalars(stmt).all()

    def get_form_source(self, workflow_id: int) -> Optional[Source]:
        """Get the form source for a given Workflow."""
        stmt = (
            select(Source)
            .join(SourceType)
            .where(Source.WorkflowId == workflow_id)
            .where(SourceType.Name == "Form")
        )
        return self.session.scalars(stmt).first()

    def name_exists(self, name) -> bool:
        """Return if a given name already exists for this Workflow."""
        if not name:
            return False
        stmt = select(Source).where(Source.Name == name)
        return bool(self.session.scalars(stmt).first())

    def delete(self, source_id: int):
        """Delete a Source and any associated form fields."""
        stmt = delete(Source).where(Source.Id == source_id)
        self.session.execute(stmt)

    def add(
        self,
        workflow_id: int,
        source_type: SourceType,
        step: int,
        file_template_id: Optional[int] = None,
        name: Optional[str] = None,
        database_id: Optional[int] = None,
        sql_text: Optional[str] = None,
        splitter: Optional[bool] = None,
        field_name: Optional[str] = None,
        key_field: Optional[str] = None,
        value_field: Optional[str] = None,
        orientation: Optional[str] = None,
        sheet_name: Optional[str] = None,
        header_row: Optional[int] = None,
    ) -> Source:
        """Add a new source of any type."""
        source = Source(
            WorkflowId=workflow_id,
            TypeId=source_type.Id,
            FileTemplateId=file_template_id,
            DatabaseId=database_id,
            SQLText=sql_text,
            Splitter=splitter,
            FieldName=field_name,
            KeyField=key_field,
            ValueField=value_field,
            Orientation=orientation,
            SheetName=sheet_name,
            HeaderRow=header_row,
            Step=step,
            Name=name,
        )
        self.session.add(source)
        self.session.flush()
        return source
