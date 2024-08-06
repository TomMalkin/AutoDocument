"""Define SQL based Sources."""

from autodoc.db import DatabaseManager, get_sql_fields
from loguru import logger

from autodoc.source.source import Source
from autodoc.metasource import MetaDatabase


class RecordSource(Source):
    """A single row of SQL data."""

    def __init__(self, source_details: dict, manager: DatabaseManager, **_) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source_details["SQLText"]
        self.database_id = source_details["DatabaseId"]

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = False

        self.meta_database = MetaDatabase(database_id=self.database_id, manager=manager)


    def load_data(self, current_data: dict) -> None:
        """
        Return the record values value using the builder dict.

        The builder dict is filtered by the field names in self.field_names, because
        we can't pass everything across. The resulting params are applied to the
        self.sql text and the scalar is returned, and then set to the self.data dict.
        """
        logger.info(f"field names are {self.field_names}")
        params = {k: v for k, v in current_data.items() if k in self.field_names}

        record = self.meta_database.record(
            sql=self.sql,
            params=params,
        )

        self.data = record.data

class RecordSetSource(Source):
    """Multi row of SQL data."""

    def __init__(self, source_details: dict, manager: DatabaseManager, **_) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source_details["SQLText"]
        self.database_id = source_details["DatabaseId"]

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = True

        self.meta_database = MetaDatabase(database_id=self.database_id, manager=manager)

    def load_data(self, current_data: dict) -> None:
        """
        Return the record values value using the builder dict.

        The builder dict is filtered by the field names in self.field_names, because
        we can't pass everything across. The resulting params are applied to the
        self.sql text and the scalar is returned, and then set to the self.data dict.
        """
        params = {k: v for k, v in current_data.items() if k in self.field_names}

        recordset = self.meta_database.recordset(
            sql=self.sql,
            params=params,
        )

        self.data = recordset.data


class RecordSetTransposeSource(Source):
    """Multirow recordset that is transposed based on 2 columns: the key and the value."""

    def __init__(self, source_details: dict, manager: DatabaseManager, **_) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source_details["SQLText"]
        self.database_id = source_details["DatabaseId"]

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = False

        self.meta_database = MetaDatabase(database_id=self.database_id, manager=manager)

        self.key_field = source_details["KeyField"]
        self.value_field = source_details["ValueField"]

        self.is_multi_record = False

    def load_data(self, current_data: dict) -> None:
        """
        Return the record values value using the builder dict.

        The builder dict is filtered by the field names in self.field_names, because
        we can't pass everything across. The resulting params are applied to the
        self.sql text and the scalar is returned, and then set to the self.data dict.
        """
        params = {k: v for k, v in current_data.items() if k in self.field_names}

        recordset = self.meta_database.recordset(
            sql=self.sql,
            params=params,
        )

        for record in recordset.data:
            key = record[self.key_field]
            value = record[self.value_field]

            self.data[key] = value
