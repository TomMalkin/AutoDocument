"""Expose the various Outcomes."""

from .html_outcome import HTMLOutcome
from .outcome import Outcome
from .pdf_outcome import PDFCombinationOutcome, PDFOutcome
from .word_outcome import WordCombinationOutcome, WordOutcome

outcome_map = {
    "HTML": HTMLOutcome,
    "Microsoft Word": WordOutcome,
    "PDF": PDFOutcome,
    "Word Combination": WordCombinationOutcome,
    "PDF Combination": PDFCombinationOutcome,
}

__all__ = [
    "HTMLOutcome",
    "WordOutcome",
    "PDFOutcome",
    "Outcome",
    "WordCombinationOutcome",
    "PDFCombinationOutcome",
]
