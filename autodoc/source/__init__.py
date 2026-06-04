"""Expose the various Sources."""

from .csv_source import CSVSourceService
from .excel_source import ExcelSourceService
from .source import SourceService as SourceService
from .sql_source import DatabaseSourceService
from .llm_source import LLMSourceService

source_service_map = {
    "Database": DatabaseSourceService,
    "CSV": CSVSourceService,
    "Excel": ExcelSourceService,
    "LLM": LLMSourceService,
}
