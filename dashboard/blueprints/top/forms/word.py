"""Define Microsoft Word based forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField, IntegerField
from wtforms.validators import InputRequired
from .mixins import FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin


class CreateWordOutcomeForm(
    FlaskForm, FileAccessorMixin, OutputFileAccessorMixin, DownloadAccessorMixin
):
    """Create Word Outcome."""

    submit = SubmitField()


class CreateWordCombinationOutcomeForm(FlaskForm):
    """Create Word Combination Outcome."""

    output_location = StringField("Output File Name", validators=[InputRequired()])
    name = StringField("Outcome Name", validators=[InputRequired()])
    submit = SubmitField()


class CreateWordSubdocumentOutcomeForm(FlaskForm):
    """Create Word Outcome."""

    input_location = StringField("Input File")
    upload_file = FileField("Upload File")
    parent_combination = SelectField("Parent Document", coerce=int)
    document_order = IntegerField("Document Order (Low to High)")
    filter_field = StringField("Filter Field")
    filter_value = StringField("Filter Value")
    submit = SubmitField()
