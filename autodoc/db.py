"""Define Database class that will store and action queries."""

from typing import List
from loguru import logger
from autodoc.config import INIT_DB_PATH, TARGET_DB_PATH

import shutil
import pendulum
import regex as re
import sqlite3
from pathlib import Path

from autodoc.containers import RecordSet, Record, RecordScalar


class Database:
    """Class to interact with a SQLite database."""

    def __init__(self, db_file: str):
        """Initialize the Database object with a connection to SQLite database file."""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def close(self):
        """Close the connection."""
        self.conn.close()

    def last_row_id(self):
        """Return the last row id."""
        return self.cursor.lastrowid

    def execute(self, query, params=None):
        """Execute a query on the database."""
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)

        self.conn.commit()

    def recordset(self, sql, params=None) -> RecordSet:
        """Execute a query on the database and return a RecordSet."""
        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)

        rows = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]

        return RecordSet(columns, rows)

    def record(self, sql, params=None) -> Record:
        """Execute a query on the database and return a Record."""
        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)

        row = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]

        return Record(columns, row)

    def record_scalar(self, sql, params=None) -> RecordScalar:
        """Execute a query on the database and return a RecordScalar."""
        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)

        row = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]

        return RecordScalar(columns, row)


class DatabaseManager:
    """Expose useful queries as methods of a database."""

    def __init__(self, db: Database):
        """Initialize the QueryManager with a database connection."""
        self.db = db

    def get_download_access_id(self):
        """Get the FileAccessId for the special download file accessor."""
        sql = """
            select Id FileAccessId
            from FileAccess
            where FileAccessTypeId = 1
        """
        record = self.db.record(sql).data
        return record["FileAccessId"]

    def delete_workflow(self, workflow_id):
        """Complete all the necessary steps to delete a workflow."""
        # get file access instances
        sql = """
            select InputFileInstanceId, OutputFileInstanceId
            from Outcome
            where WorkflowId = :workflow_id
        """
        params = {"workflow_id": workflow_id}

        instances = self.db.recordset(sql, params).data

        sql = """delete from FileAccessInstance where Id = :instance_id"""
        for row in instances:
            if row["InputFileInstanceId"]:
                params = {"instance_id": row["InputFileInstanceId"]}
                self.db.execute(sql, params)
            if row["OutputFileInstanceId"]:
                params = {"instance_id": row["OutputFileInstanceId"]}
                self.db.execute(sql, params)

        sql = "delete from Outcome where WorkflowId = :workflow_id"
        params = {"workflow_id": workflow_id}
        self.db.execute(sql, params)

        # get source file access instances
        sql = """
            select FileAccessInstanceId
            from Source
            where WorkflowId = :workflow_id
        """
        params = {"workflow_id": workflow_id}
        instances = self.db.recordset(sql, params).data

        sql = """delete from FileAccessInstance where Id = :instance_id"""
        for row in instances:
            if row["FileAccessInstanceId"]:
                params = {"instance_id": row["FileAccessInstanceId"]}
                self.db.execute(sql, params)

        # delete form fields for source
        sql = """
            delete from SourceFormField
            where SourceId in (select Id from Source where WorkflowId = :workflow_id)
        """
        params = {"workflow_id": workflow_id}
        self.db.execute(sql, params)

        sql = "delete from Source where WorkflowId = :workflow_id"
        params = {"workflow_id": workflow_id}
        self.db.execute(sql, params)

        # now delete the workflow
        sql = "delete from Workflow where Id = :workflow_id"
        params = {"workflow_id": workflow_id}
        self.db.execute(sql, params)

    def add_source(
        self,
        workflow_id,
        type_id,
        location=None,
        database_id=None,
        sql_text=None,
        splitter=False,
        field_name=None,
        key_field=None,
        value_field=None,
        step=1,
    ):
        """Add a new source line."""
        sql = """
        insert into Source
            (WorkflowId, TypeId, Location, DatabaseId, SQLText, Splitter, FieldName,
            Step, KeyField, ValueField)
        VALUES
            (:workflow_id, :type_id, :location, :database_id, :sql_text, :splitter, :field_name,
            :step, :key_field, :value_field)
        """
        params = {
            "workflow_id": workflow_id,
            "type_id": type_id,
            "location": location,
            "database_id": database_id,
            "sql_text": sql_text,
            "splitter": splitter,
            "field_name": field_name,
            "key_field": key_field,
            "value_field": value_field,
            "step": step,
        }
        self.db.execute(sql, params)

    def create_workflow(self, name):
        """Create a new workflow."""
        sql = "insert into Workflow (Name) values (:name)"
        params = {"name": name}
        self.db.execute(sql, params)
        return self.db.last_row_id()

    def get_form_source_id(self, workflow_id: int):
        """Get a source Id."""
        sql = "select Id from Source where WorkflowId = :workflow_id and TypeId = 4"
        params = params = {"workflow_id": workflow_id}
        return self.db.record_scalar(sql, params).sdatum()

    def get_workflows(self):
        """Return all workflows."""
        sql = "select Id, Name from Workflow"
        return self.db.recordset(sql).data

    def get_sources(self, workflow_id: int, step: int) -> RecordSet:
        """Get the details of the sources for a given workflow_id."""
        sql = """
            select *
            from vSource
            where WorkflowId = :workflow_id
            and Step >= :step
        """
        params = {"workflow_id": workflow_id, "step": step}
        return self.db.recordset(sql=sql, params=params)

    def get_fields(self, source_id: int) -> RecordSet:
        """Get a list of field details from the autodoc database."""
        sql = """
            select Id, FieldType, FieldName
            from SourceFormField
            where SourceId = :source_id
        """
        params = {"source_id": source_id}
        return self.db.recordset(sql=sql, params=params)

    def get_form(self, workflow_id: int) -> RecordSet:
        """Get the form details for a given workflow."""
        sql = """
            select
                SourceFormField.Id SourceFormFieldId,
                FieldType,
                SourceFormField.FieldName,
                SourceFormField.FieldLabel
            from Source
            join SourceType
                on Source.TypeId = SourceType.Id
            join SourceFormField
                on Source.Id = SourceFormField.SourceId
            where WorkflowId = :workflow_id
            and SourceType.Name = 'Form'
        """
        params = {"workflow_id": workflow_id}
        return self.db.recordset(sql=sql, params=params)

    def get_outcomes(self, workflow_id: int) -> RecordSet:
        """Return the outcomes for a given workflow."""
        sql = """
            select *
            from vOutcome
            where WorkflowId = :workflow_id
        """
        params = {"workflow_id": workflow_id}
        return self.db.recordset(sql=sql, params=params)

    def get_suboutcomes(self, parent_outcome_id: int) -> RecordSet:
        """Return any sub outcomes for a given outcome."""
        sql = """
            select Outcome.Id OutcomeId, Outcome.Name Name, InputLocation, OutputLocation,
                FileUpload,
                FilterField, FilterValue
            from Outcome
            join OutcomeType
                on Outcome.OutcomeTypeId = OutcomeType.Id
            where Outcome.ParentOutcomeId = :parent_outcome_id
            order by DocumentOrder asc
        """
        params = {"parent_outcome_id": parent_outcome_id}
        return self.db.recordset(sql=sql, params=params)

    def get_workflow_name(self, workflow_id: int) -> str:
        """Return the name of a given workflow."""
        sql = """
            select Name
            from Workflow
            where Id = :workflow_id
        """
        params = {"workflow_id": workflow_id}
        name = str(self.db.record_scalar(sql=sql, params=params).sdatum("No Name"))
        return name

    def create_workflow_instance(self, workflow_id: int, step: int) -> int:
        """Create a workflow instance in the project database and return the instance Id."""
        start_time = pendulum.now().to_iso8601_string()
        sql = """
            insert into WorkflowInstance
            (WorkflowId, StartTime, Step)
            values
            (:workflow_id, :start_time, :step)
            returning InstanceId
        """
        params = {"workflow_id": workflow_id, "start_time": start_time, "step": step}
        instance_id = self.db.record_scalar(sql=sql, params=params).datum()
        return instance_id

    def create_split_workflow_instance(
        self, workflow_id: int, parent_instance_id: int, step: int
    ) -> int:
        """Create a child workflow based on another workflow."""
        start_time = pendulum.now().to_iso8601_string()
        sql = """
            insert into WorkflowInstance
            (WorkflowId, ParentInstanceId, StartTime, Step)
            values
            (:workflow_id, :parent_instance_id, :start_time, :step)
            returning InstanceId
        """
        params = {
            "workflow_id": workflow_id,
            "parent_instance_id": parent_instance_id,
            "start_time": start_time,
            "step": step,
        }
        instance_id = self.db.record_scalar(sql=sql, params=params).datum()
        return instance_id

    def get_meta_database_details(self, database_id) -> Record:
        """Return a record of meta database details."""
        sql = """
            Select DatabaseId, Name, ConnectionString
            from DatabaseMetaSource
            where DatabaseId = :database_id
        """
        params = {"database_id": database_id}
        return self.db.record(sql=sql, params=params)

    def get_meta_databases(self) -> RecordSet:
        """Return a record of meta database details."""
        sql = """
            Select DatabaseId, Name, ConnectionString
            from DatabaseMetaSource
        """
        return self.db.recordset(sql=sql)

    def add_meta_database(self, name, connection_string):
        """Add a meta database."""
        sql = """
            insert into DatabaseMetaSource
            (Name, ConnectionString)
            values
            (:name, :connection_string)
        """
        params = {"name": name, "connection_string": connection_string}
        self.db.execute(sql, params)

    def delete_meta_database(self, database_id):
        """Add a meta database."""
        sql = """
            delete from DatabaseMetaSource
            where DatabaseId = :database_id
        """
        params = {"database_id": database_id}
        self.db.execute(sql, params)

    def get_posix_filesystems(self) -> RecordSet:
        """Return a record set of all posix filesystems."""
        sql = """
            Select
                FileAccess.Id FileAccessId,
                FileAccessType.Name FileAccessType,
                LocalPath,
                RemotePath,
                TopLevel,
                URL,
                UserName,
                Password
            from FileAccess
            inner join FileAccessType
                on FileAccess.FileAccessTypeId = FileAccessType.Id
            where FileAccessType.Name = 'Linux Share'
        """
        return self.db.recordset(sql)

    def get_windows_filesystems(self) -> RecordSet:
        """Return a record set of all windows filesystems."""
        sql = """
            Select
                FileAccess.Id FileAccessId,
                FileAccessType.Name FileAccessType,
                LocalPath,
                RemotePath,
                TopLevel,
                URL,
                UserName,
                Password
            from FileAccess
            inner join FileAccessType
                on FileAccess.FileAccessTypeId = FileAccessType.Id
            where FileAccessType.Name = 'Windows Share'
        """
        return self.db.recordset(sql)

    def get_s3_filesystems(self) -> RecordSet:
        """Return a record set of all windows filesystems."""
        sql = """
            Select
                FileAccess.Id FileAccessId,
                FileAccessType.Name FileAccessType,
                LocalPath,
                RemotePath,
                TopLevel,
                URL,
                UserName,
                Password
            from FileAccess
            inner join FileAccessType
                on FileAccess.FileAccessTypeId = FileAccessType.Id
            where FileAccessType.Name = 'S3'
        """
        return self.db.recordset(sql)

    def get_sharepoints(self) -> RecordSet:
        """Return a record set of all windows filesystems."""
        sql = """
            Select
                FileAccess.Id FileAccessId,
                FileAccessType.Name FileAccessType,
                LocalPath,
                RemotePath,
                TopLevel,
                URL,
                UserName,
                Password
            from FileAccess
            inner join FileAccessType
                on FileAccess.FileAccessTypeId = FileAccessType.Id
            where FileAccessType.Name = 'SharePoint'
        """
        return self.db.recordset(sql)

    def add_posix_filesystem(self, local_path, remote_path):
        """Add a new posix filesystem to the database."""
        sql = """
            INSERT INTO FileAccess (
                FileAccessTypeId,
                LocalPath,
                RemotePath
            ) VALUES (
                3,
                :local_path,
                :remote_path
            )
        """
        params = {"local_path": local_path, "remote_path": remote_path}
        self.db.execute(sql, params)

    def add_windows_filesystem(self, local_path, remote_path):
        """Add a new windows filesystem to the database."""
        sql = """
            INSERT INTO FileAccess (
                FileAccessTypeId,
                LocalPath,
                RemotePath
            ) VALUES (
                2,
                :local_path,
                :remote_path
            )
        """
        params = {"local_path": local_path, "remote_path": remote_path}
        self.db.execute(sql, params)

    def add_s3(self, url, username, password):
        """Add a new windows filesystem to the database."""
        sql = """
            INSERT INTO FileAccess (
                FileAccessTypeId,
                URL,
                Username,
                Password
            ) VALUES (
                4,
                :url,
                :username,
                :password
            )
        """
        params = {"url": url, "username": username, "password": password}
        self.db.execute(sql, params)

    def add_sharepoint(self, url, library, username, password):
        """Add a new windows filesystem to the database."""
        sql = """
            INSERT INTO FileAccess (
                FileAccessTypeId,
                URL,
                RemotePath,
                Username,
                Password
            ) VALUES (
                5,
                :url,
                :library,
                :username,
                :password
            )
        """
        params = {"url": url, "username": username, "password": password, "library": library}
        self.db.execute(sql, params)

    def add_file_access_instance(self, file_access_id, location=None, bucket=None, outcome_id=None):
        """Add a file access instance and return the inserted Id."""
        sql = """
            insert into FileAccessInstance
            (FileAccessId, OutcomeId, Location, Bucket)
            values
            (:file_access_id, :outcome_id, :location, :bucket)
        """
        params = {
            "file_access_id": file_access_id,
            "outcome_id": outcome_id,
            "location": location,
            "bucket": bucket,
        }
        self.db.execute(sql, params)

        return self.db.last_row_id()

    def remove_file_access(self, file_access_id: int):
        """Remove a file system."""
        sql = """
            delete from FileAccess
            where Id = :file_access_id
        """
        params = {"file_access_id": file_access_id}
        self.db.execute(sql, params)


def initialise_database(initial_db=None, target_db=None):
    """Initialise a database for example if running for the first time."""
    initial_db = initial_db or INIT_DB_PATH or "./init/initial_database.db"
    target_db = target_db or TARGET_DB_PATH or "./database/autodoc.db"

    if Path(target_db).is_file():
        logger.info("Database already initialised.")
        return

    logger.info(f"Initialising clean database {target_db}")
    shutil.copy(initial_db, target_db)


def get_sql_fields(sql: str) -> List:
    """Return the sql fields that are required to render sql text."""
    pattern = r"(?<=[\s\(]:)([A-Z0-9a-z\_]*)"
    field_names = re.findall(pattern, sql)
    return field_names
