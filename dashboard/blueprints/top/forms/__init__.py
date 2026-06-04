"""Expose forms."""

from .csv import CreateCSVSourceForm
from .dynamic import get_form as get_form

from .excel import CreateExcelSourceForm
from .form_field import CreateFormFieldForm as CreateFormFieldForm
from .llm import CreateLLMSourceForm as CreateLLMSourceForm
from .meta import CreateMetaDatabase as CreateMetaDatabase
from .pdf import CreatePDFOutcomeForm as CreatePDFOutcomeForm

from .sql import CreateDatabaseSourceForm
from .text import CreateTextOutcomeForm as CreateTextOutcomeForm
from .word import CreateWordOutcomeForm as CreateWordOutcomeForm
from .workflow import CreateWorkflowForm as CreateWorkflowForm

ADD_SOURCE_FORMS = {
    "LLM": CreateLLMSourceForm,
    "Database": CreateDatabaseSourceForm,
    "CSV": CreateCSVSourceForm,
    "Excel": CreateExcelSourceForm,
}

ADD_OUTCOME_FORMS = {
    "Text": CreateTextOutcomeForm,
    "Microsoft Word": CreateWordOutcomeForm,
    "PDF": CreatePDFOutcomeForm,
}
