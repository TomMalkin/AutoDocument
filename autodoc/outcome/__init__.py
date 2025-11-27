"""Expose the various Outcomes."""

from .text_outcome import TextOutcomeService
from .outcome import OutcomeService as OutcomeService
from .pdf_outcome import PDFOutcomeService
from .word_outcome import WordOutcomeService

outcome_service_map = {
    "Text": TextOutcomeService,
    "Microsoft Word": WordOutcomeService,
    "PDF": PDFOutcomeService,
}
