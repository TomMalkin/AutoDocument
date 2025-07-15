"""Define SQL based Sources."""

import regex as re

from autodoc.data.tables import Source
from autodoc.metasource import MetaDatabase

from .source import SourceService


def get_sql_fields(sql: str) -> list:
    """Return the sql fields that are required to render sql text."""
    pattern = r"(?<=[\s\(]:)([A-Z0-9a-z\_]*)"
    field_names = re.findall(pattern, sql)
    return field_names


class RecordSourceService(SourceService):
    """A single row of SQL data."""

    def __init__(self, source: Source) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source.SQLText
        self.database_id = source.DatabaseId

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = False

        self.meta_database = MetaDatabase(database=self.source.database)

    def load_data(self, current_data: dict) -> None:
        """
        Return the record values value using the builder dict.

        The builder dict is filtered by the field names in self.field_names, because
        we can't pass everything across. The resulting params are applied to the
        self.sql text and the scalar is returned, and then set to the self.data dict.
        """
        params = {k: v for k, v in current_data.items() if k in self.field_names}

        record = self.meta_database.record(
            sql=self.sql,
            params=params,
        )

        self.data = record.data


class RecordSetSourceService(SourceService):
    """Multiple rows of SQL data."""

    def __init__(self, source: Source) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source.SQLText
        self.database_id = source.DatabaseId

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = True

        self.meta_database = MetaDatabase(database=self.source.database)

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


class RecordSetTransposeSourceService(SourceService):
    """Multirow recordset that is transposed based on 2 columns: the key and the value."""

    def __init__(self, source: Source) -> None:
        """Source several values from a single record from a SQL query."""
        self.data = {}

        self.sql = source.SQLText
        self.database_id = source.DatabaseId

        self.field_names = get_sql_fields(sql=self.sql)
        self.is_multi_record = False

        self.meta_database = MetaDatabase(database=self.source.database)

        self.key_field = source.KeyField
        self.value_field = source.ValueField

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
