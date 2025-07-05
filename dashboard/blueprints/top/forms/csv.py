"""Define CSV forms."""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,  # type: ignore
    RadioField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, InputRequired

from .mixins import FileAccessorMixin


class CreateCSVRecordSourceForm(FlaskForm, FileAccessorMixin):
    """Create a CSV Record Form."""

    orientation = SelectField(
        "Orientation", choices=[(0, "Horizontal"), (1, "Vertical")], validators=[DataRequired()]
    )
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()


class CreateCSVTableSourceForm(FlaskForm, FileAccessorMixin):
    """Create a CSV Table Form."""

    step = IntegerField("Step", validators=[InputRequired()], default=1)
    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])
    field_name = StringField("Field Name")
    submit = SubmitField()
