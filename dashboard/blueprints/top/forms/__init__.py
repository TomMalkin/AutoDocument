"""Expose forms."""

from .csv import CreateCSVRecordSourceForm as CreateCSVRecordSourceForm
from .csv import CreateCSVTableSourceForm as CreateCSVTableSourceForm
from .dynamic import get_form as get_form
from .excel import (
    CreateExcelRecordSourceForm as CreateExcelRecordSourceForm,
    CreateExcelTableSourceForm as CreateExcelTableSourceForm,
)
from .form_field import CreateFormFieldForm as CreateFormFieldForm
from .text import CreateTextOutcomeForm as CreateTextOutcomeForm
from .meta import CreateMetaDatabase as CreateMetaDatabase
from .pdf import CreatePDFOutcomeForm as CreatePDFOutcomeForm
from .sql import CreateRecordSetSourceForm as CreateRecordSetSourceForm
from .sql import CreateRecordSetTransposeSourceForm as CreateRecordSetTransposeSourceForm
from .sql import CreateRecordSourceForm as CreateRecordSourceForm
from .word import CreateWordOutcomeForm as CreateWordOutcomeForm
from .workflow import CreateWorkflowForm as CreateWorkflowForm
from .llm import CreateLLMSourceForm as CreateLLMSourceForm

ADD_SOURCE_FORMS = {
    "SQL Record": CreateRecordSourceForm,
    "SQL RecordSet": CreateRecordSetSourceForm,
    "SQL RecordSet Transpose": CreateRecordSetTransposeSourceForm,
    "CSVRecord": CreateCSVRecordSourceForm,
    "CSVTable": CreateCSVTableSourceForm,
    "ExcelRecord": CreateExcelRecordSourceForm,
    "ExcelTable": CreateExcelTableSourceForm,
    "LLM": CreateLLMSourceForm,
}

ADD_OUTCOME_FORMS = {
    "Text": CreateTextOutcomeForm,
    "Microsoft Word": CreateWordOutcomeForm,
    "PDF": CreatePDFOutcomeForm,
}
