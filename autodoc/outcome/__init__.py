"""Expose the various Outcomes."""

from .html_outcome import HTMLOutcome
from .outcome import Outcome
from .pdf_outcome import PDFOutcome
from .word_outcome import WordOutcome

outcome_map = {
    "HTML": HTMLOutcome,
    "Microsoft Word": WordOutcome,
    "PDF": PDFOutcome,
}

__all__ = [
    "HTMLOutcome",
    "WordOutcome",
    "PDFOutcome",
    "Outcome",
]
