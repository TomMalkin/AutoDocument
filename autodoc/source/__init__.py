"""Expose the various Sources."""

from .csv_source import CSVRecord, CSVTable
from .form_source import FormSource
from .sql_source import RecordSetSource, RecordSetTransposeSource, RecordSource
from .excel_source import ExcelRecord, ExcelTable

source_map = {
    "SQL Record": RecordSource,
    "SQL RecordSet": RecordSetSource,
    "SQL RecordSet Transpose": RecordSetTransposeSource,
    "CSVRecord": CSVRecord,
    "CSVTable": CSVTable,
    "ExcelRecord": ExcelRecord,
    "ExcelTable": ExcelTable,
}

__all__ = [
    "RecordSource",
    "RecordSetSource",
    "FormSource",
    "RecordSetTransposeSource",
    "CSVRecord",
    "CSVTable",
    "ExcelRecord",
    "ExcelTable",
]
