"""Expose the various Outcomes."""

from .html_outcome import HTMLOutcomeService
from .outcome import OutcomeService
from .pdf_outcome import PDFOutcomeService
from .word_outcome import WordOutcomeService

outcome_service_map = {
    "HTML": HTMLOutcomeService,
    "Microsoft Word": WordOutcomeService,
    "PDF": PDFOutcomeService,
}

__all__ = [
    "HTMLOutcomeService",
    "WordOutcomeService",
    "PDFOutcomeService",
    "OutcomeService",
]
