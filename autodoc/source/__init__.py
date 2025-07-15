"""Expose the various Sources."""

from .csv_source import CSVRecordSourceService, CSVTableSourceService
from .excel_source import ExcelRecordSourceService, ExcelTableSourceService
from .source import SourceService as SourceService
from .sql_source import RecordSetSourceService, RecordSetTransposeSourceService, RecordSourceService

source_service_map = {
    "SQL Record": RecordSourceService,
    "SQL RecordSet": RecordSetSourceService,
    "SQL RecordSet Transpose": RecordSetTransposeSourceService,
    "CSVRecord": CSVRecordSourceService,
    "CSVTable": CSVTableSourceService,
    "ExcelRecord": ExcelRecordSourceService,
    "ExcelTable": ExcelTableSourceService,
}
