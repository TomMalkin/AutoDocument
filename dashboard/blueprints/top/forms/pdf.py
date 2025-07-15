"""Define PDF forms."""

from flask_wtf import FlaskForm
from wtforms import SubmitField

from .mixins import DownloadAccessorMixin, FileAccessorMixin, OutputFileAccessorMixin


class CreatePDFOutcomeForm(
    FlaskForm, FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
):
    """Create a PDF Outcome."""

    submit = SubmitField()
