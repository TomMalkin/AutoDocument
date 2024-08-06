"""Expose the various Sources."""

from .csv_source import CSVRecord, CSVTable
from .form_source import FormSource
from .sql_source import RecordSetSource, RecordSetTransposeSource, RecordSource

source_map = {
    "SQL Record": RecordSource,
    "SQL RecordSet": RecordSetSource,
    "SQL RecordSet Transpose": RecordSetTransposeSource,
    "CSVRecord": CSVRecord,
    "CSVTable": CSVTable,
}

__all__ = [
    "RecordSource",
    "RecordSetSource",
    "FormSource",
    "RecordSetTransposeSource",
    "CSVRecord",
    "CSVTable",
]
