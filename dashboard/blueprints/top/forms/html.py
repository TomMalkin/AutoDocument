"""Define HTML forms."""

from flask_wtf import FlaskForm
from wtforms import SubmitField

from .mixins import DownloadAccessorMixin, FileAccessorMixin, OutputFileAccessorMixin


class CreateHTMLOutcomeForm(
    FlaskForm, FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
):
    """Create HTML Outcome."""

    submit = SubmitField()
