"""Define the ORM for views in the sqlite database."""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import mapped_column

from .base import Base


class VFileAccessor(Base):
    """
    ORM Mapping to the view vFileAccessors.

    CREATE VIEW vFileAccessors
    (FileAccessId, FileAccessTypeId, LocalPath, RemotePath, URL, FileAccessTypeName)
    as
    select
        FileAccess.Id FileAccessId,
        FileAccessTypeId,
        LocalPath,
        RemotePath,
        URL,
        FileAccessType.Name FileAccessTypeName
    from FileAccess
    inner join FileAccessType
        on FileAccess.FileAccessTypeId = FileAccessType.Id
    where FileAccessType.Name != "Download"
    """

    __tablename__ = "vFileAccessors"

    FileAccessId = mapped_column(Integer, primary_key=True)
    FileAccessTypeId = mapped_column(Integer)
    LocalPath = mapped_column(String)
    RemotePath = mapped_column(String)
    URL = mapped_column(String)
    FileAccessTypeName = mapped_column(String)


class VSource(Base):
    """
    SQLAlchemy ORM class mapping to the database view 'vSource'.

    This class should be treated as READ-ONLY in application logic,
    as writing directly to views is often not supported or requires
    specific database triggers (e.g., INSTEAD OF triggers in SQLite).

    The primary key 'SourceId' is assumed to be unique for each row
    returned by the view, derived from the underlying 'Source' table's Id.
    """

    __tablename__ = "vSource"  # The exact name of the database view

    # --- Primary Key ---
    # Mapped from Source.Id. Assumed to be unique within the view results.
    SourceId = mapped_column(Integer, primary_key=True)

    # --- Columns from Source table ---
    WorkflowId = mapped_column(Integer)  # Assuming foreign key to a Workflow table
    SourceName = mapped_column(String)
    SheetName = mapped_column(String)
    HeaderRow = mapped_column(Integer)
    SQLText = mapped_column(Text)  # Using Text for potentially long SQL queries
    DatabaseId = mapped_column(Integer)  # Assuming foreign key to a Database table
    FieldName = mapped_column(String)
    Splitter = mapped_column(String)  # Assuming String, adjust if numeric
    Step = mapped_column(Integer)
    KeyField = mapped_column(String)
    ValueField = mapped_column(String)
    Orientation = mapped_column(String)

    # --- Columns from SourceType table ---
    TypeName = mapped_column(String)
    IsFile = mapped_column(Boolean)
    IsMulti = mapped_column(Boolean)

    # --- Columns from DatabaseMetaSource table ---
    DatabaseName = mapped_column(String)

    # --- Columns from FileAccessInstance table ---
    Location = mapped_column(String)
    Bucket = mapped_column(String)
    FileAccessId = mapped_column(Integer)  # Assuming foreign key to FileAccess table

    # --- Columns from FileAccess table ---
    LocalPath = mapped_column(String)
    RemotePath = mapped_column(String)
    URL = mapped_column(String)
    Username = mapped_column(String)
    Password = mapped_column(String)  # Note: Handle password security appropriately

    # --- Columns from FileAccessType table ---
    FileAccessTypeName = mapped_column(String)

    # Optional: Define that this is not a "real" table that SQLAlchemy
    # should try to create or modify. Useful if using Base.metadata.create_all()
    # although mapping to a view usually implies the schema already exists.
    __table_args__ = {"info": dict(is_view=True)}

    def __repr__(self):
        # Optional: Provide a helpful representation for debugging
        return f"<VSource(SourceId={self.SourceId}, TypeName='{self.TypeName}', SourceName='{self.SourceName}')>"


class VOutcome(Base):
    """
    SQLAlchemy ORM class mapping to the database view 'vOutcome'.

    This class should be treated as READ-ONLY in application logic.
    Writing directly to views requires specific database configurations
    (e.g., INSTEAD OF triggers) that are not handled by this mapping.

    The primary key 'OutcomeId' is assumed to be unique for each row
    returned by the view, derived from the underlying 'Outcome' table's Id.
    Columns derived from the LEFT JOIN to 'vFileAccessInstance' may be NULL.
    """

    __tablename__ = "vOutcome"  # The exact name of the database view

    # --- Primary Key ---
    # Mapped from Outcome.Id. Assumed to be unique within the view results.
    OutcomeId = mapped_column(Integer, primary_key=True)

    # --- Columns from Outcome table ---
    WorkflowId = mapped_column(Integer)  # Assuming foreign key to a Workflow table
    FilterField = mapped_column(String)
    FilterValue = mapped_column(String)
    ParentOutcomeId = mapped_column(Integer, nullable=True)  # Can be null if no parent
    DocumentOrder = mapped_column(Integer)  # Assuming integer order
    OutcomeName = mapped_column(String)
    InputFileInstanceId = mapped_column(
        Integer, nullable=True
    )  # FK, potentially null via LEFT JOIN
    OutputFileInstanceId = mapped_column(
        Integer, nullable=True
    )  # FK, potentially null via LEFT JOIN

    # --- Columns from OutcomeType table ---
    OutcomeTypeName = mapped_column(String)
    IsFile = mapped_column(Boolean)

    # --- Columns from InputFileAccessInstance (vFileAccessInstance alias) ---
    # These columns can be NULL because of the LEFT JOIN
    InputFileLocation = mapped_column(String, nullable=True)
    InputFileBucket = mapped_column(String, nullable=True)
    InputLocalPath = mapped_column(String, nullable=True)
    InputRemotePath = mapped_column(String, nullable=True)
    InputURL = mapped_column(String, nullable=True)
    InputFileTypeName = mapped_column(String, nullable=True)  # Mapped from vFileAccessInstance.Name
    InputUserName = mapped_column(String, nullable=True)
    InputPassword = mapped_column(
        String, nullable=True
    )  # Note: Handle password security appropriately

    # --- Columns from OutputFileAccessInstance (vFileAccessInstance alias) ---
    # These columns can also be NULL because of the LEFT JOIN
    OutputFileLocation = mapped_column(String, nullable=True)
    OutputFileBucket = mapped_column(String, nullable=True)
    OutputLocalPath = mapped_column(String, nullable=True)
    OutputRemotePath = mapped_column(String, nullable=True)
    OutputURL = mapped_column(String, nullable=True)
    OutputFileTypeName = mapped_column(
        String, nullable=True
    )  # Mapped from vFileAccessInstance.Name
    OutputUserName = mapped_column(String, nullable=True)
    OutputPassword = mapped_column(
        String, nullable=True
    )  # Note: Handle password security appropriately

    # Optional: Define that this is not a "real" table that SQLAlchemy
    # should try to create or modify.
    __table_args__ = {"info": dict(is_view=True)}

    def __repr__(self):
        # Optional: Provide a helpful representation for debugging
        return (
            f"<VOutcome(OutcomeId={self.OutcomeId}, "
            f"OutcomeTypeName='{self.OutcomeTypeName}', "
            f"OutcomeName='{self.OutcomeName}')>"
        )
