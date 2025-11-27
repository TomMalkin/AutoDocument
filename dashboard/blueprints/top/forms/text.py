"""Define Text forms."""

from flask_wtf import FlaskForm
from wtforms import SubmitField

from .mixins import DownloadAccessorMixin, FileAccessorMixin, OutputFileAccessorMixin


class CreateTextOutcomeForm(
    FlaskForm, FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
):
    """Create Text Outcome."""

    submit = SubmitField()
