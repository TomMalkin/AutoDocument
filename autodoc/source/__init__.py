"""Expose the various Sources."""

from .csv_source import CSVRecordSourceService, CSVTableSourceService
from .excel_source import ExcelRecordSourceService, ExcelTableSourceService
from .sql_source import RecordSetSourceService, RecordSetTransposeSourceService, RecordSourceService
from .source import SourceService as SourceService

source_service_map = {
    "SQL Record": RecordSourceService,
    "SQL RecordSet": RecordSetSourceService,
    "SQL RecordSet Transpose": RecordSetTransposeSourceService,
    "CSVRecord": CSVRecordSourceService,
    "CSVTable": CSVTableSourceService,
    "ExcelRecord": ExcelRecordSourceService,
    "ExcelTable": ExcelTableSourceService,
}

# __all__ = [
#     "RecordSourceService",
#     "RecordSetSourceService",
#     "RecordSetTransposeSourceService",
#     "CSVRecordSourceService",
#     "CSVTableSourceService",
#     "ExcelRecordSourceService",
#     "ExcelTableSourceService",
# ]
