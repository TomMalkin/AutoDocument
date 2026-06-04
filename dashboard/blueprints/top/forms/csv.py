"""Define CSV forms."""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    RadioField,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired

from .mixins import FileAccessorMixin


class CreateCSVSourceForm(FlaskForm, FileAccessorMixin):
    """Create a CSV Form."""

    step = IntegerField("Step", validators=[InputRequired()], default=1)
    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])
    field_name = StringField("Field Name")
    submit = SubmitField()
