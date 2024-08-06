"""Define HTML forms."""

from wtforms import SubmitField
from .mixins import FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
from flask_wtf import FlaskForm


class CreateHTMLOutcomeForm(
    FlaskForm, FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
):
    """Create HTML Outcome."""

    submit = SubmitField()
