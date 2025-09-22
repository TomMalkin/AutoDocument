"""Define all ORM tables from the sqlite database."""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SQLFields(Base):
    """
    List replaceable fields found in SQL text sources.

    For example, if a statement is uploaded with:

    Select Client.Name
    from Client
    where Client.Id = :client_id

    Then 'client_id' is extracted and saved in this table.
    """

    __tablename__ = "SQLFields"
    Id: Mapped[int] = mapped_column(primary_key=True)
    SourceId: Mapped[int] = mapped_column(ForeignKey("Source.Id"))
    FieldName: Mapped[str] = mapped_column(Text)

    source: Mapped["Source"] = relationship(back_populates="fields")


class FormField(Base):
    """Represents a field in a form, associated with a workflow."""

    __tablename__ = "FormField"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    WorkflowId: Mapped[int] = mapped_column(ForeignKey("Workflow.Id"))
    FieldType: Mapped[str] = mapped_column(Text, nullable=False)
    FieldName: Mapped[str] = mapped_column(Text)
    FieldLabel: Mapped[str] = mapped_column(Text)

    workflow: Mapped["Workflow"] = relationship(back_populates="form_fields")


class Workflow(Base):
    """
    Represents a workflow template.

    This links to all the form fields, sources and outcomes that will be processed
    when the Workflow is run.

    Note, the table is called Workflow, but we will call it Workflow to differentiate between
    this and the Workflow object defined by the autodoc library.
    """

    __tablename__ = "Workflow"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    instances: Mapped[list["WorkflowInstance"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )
    sources: Mapped[list["Source"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )
    outcomes: Mapped[list["Outcome"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )
    form_fields: Mapped[list["FormField"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan"
    )


class WorkflowInstance(Base):
    """Represents a specific instance of a workflow, tracking its progress and data."""

    __tablename__ = "WorkflowInstance"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ParentInstanceId: Mapped[int] = mapped_column(nullable=True)
    WorkflowId: Mapped[int] = mapped_column(ForeignKey("Workflow.Id"), nullable=True)
    StartTime: Mapped[float] = mapped_column(Numeric, nullable=True)
    EndTime: Mapped[str] = mapped_column(Text, nullable=True)
    Completed: Mapped[bool] = mapped_column(Boolean, default=False)
    Data: Mapped[str] = mapped_column(Text, nullable=True)
    Step: Mapped[int] = mapped_column(default=1)

    workflow: Mapped["Workflow"] = relationship(back_populates="instances")
    # events: Mapped[list["WorkflowInstanceEvent"]] = relationship(back_populates="instance")


# class WorkflowInstanceEvent(Base):
#     """Represents an event within a workflow instance, linking to sources and outcomes."""
#
#     __tablename__ = "WorkflowInstanceEvent"
#     Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     WorkflowInstanceId: Mapped[int] = mapped_column(ForeignKey("WorkflowInstance.InstanceId"))
#     SourceId: Mapped[int] = mapped_column(ForeignKey("Source.Id"))
#     OutcomeId: Mapped[int] = mapped_column(ForeignKey("Outcome.Id"))
#     SourceData: Mapped[str] = mapped_column(Text)
#     SourceDataOngoing: Mapped[str] = mapped_column(Text)
#     OutcomeLocation: Mapped[str] = mapped_column(Text)
#
#     instance: Mapped["WorkflowInstance"] = relationship(back_populates="events")
#     source: Mapped["Source"] = relationship(back_populates="events")
#     outcome: Mapped["Outcome"] = relationship(back_populates="events")


class DatabaseMetaSource(Base):
    """Stores metadata for database sources, including connection strings."""

    __tablename__ = "DatabaseMetaSource"
    Id: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ConnectionString: Mapped[str] = mapped_column(Text, nullable=False)

    sources: Mapped[list["Source"]] = relationship(back_populates="database")


class OutcomeType(Base):
    """Defines types of outcomes, such as file-based outcomes."""

    __tablename__ = "OutcomeType"
    Id: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False)
    IsFile: Mapped[bool] = mapped_column(default=True)

    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="outcome_type")


class SourceType(Base):
    """Defines types of sources, indicating properties like slowness, file-based, or multi-value."""

    __tablename__ = "SourceType"
    Id: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False)
    IsSlow: Mapped[bool]
    IsFile: Mapped[bool]
    IsMulti: Mapped[bool]

    sources: Mapped[list["Source"]] = relationship(back_populates="source_type")


class StorageType(Base):
    """Defines types of storage, like local, remote, or cloud."""

    __tablename__ = "StorageType"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    storage_instances: Mapped[list["StorageInstance"]] = relationship(back_populates="storage_type")


class StorageInstance(Base):
    """Represents a specific instance of a storage type, with path and access details."""

    __tablename__ = "StorageInstance"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    StorageTypeId: Mapped[int] = mapped_column(ForeignKey("StorageType.Id"))
    LocalPath: Mapped[str] = mapped_column(Text, nullable=True)
    RemotePath: Mapped[str] = mapped_column(Text, nullable=True)
    TopLevel: Mapped[str] = mapped_column(Text, nullable=True)
    URL: Mapped[str] = mapped_column(Text, nullable=True)
    Username: Mapped[str] = mapped_column(Text, nullable=True)
    Password: Mapped[str] = mapped_column(Text, nullable=True)

    storage_type: Mapped["StorageType"] = relationship(back_populates="storage_instances")
    file_templates: Mapped[list["FileTemplate"]] = relationship(back_populates="storage_instance")


class FileTemplate(Base):
    """Defines templates for files, linking to storage instances."""

    __tablename__ = "FileTemplate"
    Id: Mapped[int] = mapped_column(primary_key=True)
    StorageInstanceId: Mapped[int] = mapped_column(ForeignKey("StorageInstance.Id"))
    Location: Mapped[str] = mapped_column(Text, nullable=True)
    Bucket: Mapped[str] = mapped_column(Text, nullable=True)

    storage_instance: Mapped["StorageInstance"] = relationship(back_populates="file_templates")

    input_file_template: Mapped["Outcome"] = relationship(
        back_populates="input_file_template", foreign_keys="Outcome.InputFileTemplateId"
    )
    output_file_template: Mapped["Outcome"] = relationship(
        back_populates="output_file_template", foreign_keys="Outcome.OutputFileTemplateId"
    )

    source: Mapped["Source"] = relationship(back_populates="file_template")

    @property
    def is_download(self) -> bool:
        """Return if this file template should be added to the download container."""
        return self.StorageInstanceId == -1

    def get_root(self) -> str:
        """Get the root for a File Template Service."""
        return self.storage_instance.LocalPath or self.Bucket or self.storage_instance.RemotePath


class Outcome(Base):
    """Represents a specific outcome of a workflow."""

    __tablename__ = "Outcome"
    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    WorkflowId: Mapped[int] = mapped_column(ForeignKey("Workflow.Id"))
    OutcomeTypeId: Mapped[int] = mapped_column(ForeignKey("OutcomeType.Id"))
    FileUpload: Mapped[bool] = mapped_column(default=False)
    FilterField: Mapped[str] = mapped_column(Text, nullable=True)
    FilterValue: Mapped[str] = mapped_column(Text, nullable=True)
    Name: Mapped[str] = mapped_column(Text, nullable=True)
    ParentOutcomeId: Mapped[int] = mapped_column(nullable=True)
    DocumentOrder: Mapped[int] = mapped_column(nullable=True)
    InputFileTemplateId: Mapped[int] = mapped_column(ForeignKey("FileTemplate.Id"), nullable=True)
    OutputFileTemplateId: Mapped[int] = mapped_column(ForeignKey("FileTemplate.Id"), nullable=True)
    DownloadName: Mapped[str] = mapped_column(nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="outcomes")
    outcome_type: Mapped["OutcomeType"] = relationship(back_populates="outcomes")
    # events: Mapped[list["WorkflowInstanceEvent"]] = relationship(back_populates="outcome")
    input_file_template: Mapped[Optional["FileTemplate"]] = relationship(
        back_populates="input_file_template", foreign_keys=InputFileTemplateId
    )
    output_file_template: Mapped[Optional["FileTemplate"]] = relationship(
        back_populates="output_file_template", foreign_keys=OutputFileTemplateId
    )

    @property
    def is_download(self) -> bool:
        """Return if this outcome is downloaded."""
        return not self.output_file_template or self.output_file_template.StorageInstanceId == -1


class Source(Base):
    """Represents a data source for a workflow."""

    __tablename__ = "Source"
    Id: Mapped[int] = mapped_column(primary_key=True)
    WorkflowId: Mapped[int] = mapped_column(ForeignKey("Workflow.Id"))
    TypeId: Mapped[int] = mapped_column(ForeignKey("SourceType.Id"))
    FileTemplateId: Mapped[int] = mapped_column(ForeignKey("FileTemplate.Id"), nullable=True)
    # ZIndex: Mapped[int]
    DatabaseId: Mapped[int] = mapped_column(ForeignKey(DatabaseMetaSource.Id), nullable=True)
    SQLText: Mapped[str] = mapped_column(Text, nullable=True)
    Splitter: Mapped[int] = mapped_column(default=0)
    FieldName: Mapped[str] = mapped_column(Text, nullable=True)
    Step: Mapped[int] = mapped_column(default=1, nullable=False)
    KeyField: Mapped[str] = mapped_column(Text, nullable=True)
    ValueField: Mapped[str] = mapped_column(Text, nullable=True)
    Orientation: Mapped[str] = mapped_column(Text, nullable=True)
    Name: Mapped[str] = mapped_column(Text, nullable=True)
    SheetName: Mapped[str] = mapped_column(Text, nullable=True)
    HeaderRow: Mapped[int] = mapped_column(nullable=True)

    LLMId: Mapped[int] = mapped_column(ForeignKey("LLM.Id"), nullable=True)
    llm: Mapped["LLM"] = relationship("LLM", back_populates="sources")

    LLMPromptTemplate: Mapped[str] = mapped_column(Text, nullable=True)
    LLMSystemPrompt: Mapped[str] = mapped_column(Text, nullable=True)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="sources")
    source_type: Mapped["SourceType"] = relationship("SourceType", back_populates="sources")
    database: Mapped["DatabaseMetaSource"] = relationship(
        "DatabaseMetaSource", back_populates="sources"
    )
    file_template: Mapped["FileTemplate"] = relationship("FileTemplate", back_populates="source")
    fields: Mapped[list["SQLFields"]] = relationship(back_populates="source")

    @property
    def system_prompt(self):
        """Get the system prompt which may have been overridden by the source."""
        return self.LLMSystemPrompt or self.llm.SystemPrompt


class LLMProvider(Base):
    """Options for an AI provider."""

    __tablename__ = "LLMProvider"
    Id: Mapped[int] = mapped_column(primary_key=True)
    # the name that will be user facing
    CommonName: Mapped[str] = mapped_column(Text, nullable=False)

    # the option used to create langchain's init_chat_model
    LangChainName: Mapped[str] = mapped_column(Text, nullable=False)
    llms: Mapped[list["LLM"]] = relationship(back_populates="provider")


class LLM(Base):
    """Represents a metadata LLM option."""

    __tablename__ = "LLM"
    Id: Mapped[int] = mapped_column(primary_key=True)
    # Name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    ProviderId: Mapped[int] = mapped_column(ForeignKey("LLMProvider.Id"), nullable=False)
    provider: Mapped["LLMProvider"] = relationship("LLMProvider", back_populates="llms")

    ModelName: Mapped[str] = mapped_column(Text, nullable=False)
    BaseURL: Mapped[str] = mapped_column(Text, nullable=True)
    APIKey: Mapped[str] = mapped_column(Text, nullable=True)

    # this is the default system prompt unless another is specified at the source level
    SystemPrompt: Mapped[str] = mapped_column(Text, nullable=True)

    sources: Mapped[list["Source"]] = relationship(back_populates="llm")
