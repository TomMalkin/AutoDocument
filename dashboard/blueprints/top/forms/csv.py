"""Define CSV forms."""

from .mixins import FileAccessorMixin
from flask_wtf import FlaskForm
from wtforms import IntegerField  # type: ignore
from wtforms import SelectField, StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, InputRequired  # type: ignore


class CreateCSVRecordSourceForm(FlaskForm, FileAccessorMixin):
    """Create a Record Source."""

    orientation = SelectField(
        "Orientation",
        choices=[(0, "Horizontal"), (1, "Vertical")],
        validators=[DataRequired()]
    )
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()

class CreateCSVTableSourceForm(FlaskForm, FileAccessorMixin):
    """Create a CSV Table Form."""

    step = IntegerField("Step", validators=[InputRequired()], default=1)
    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])
    field_name = StringField("Field Name")
    submit = SubmitField()

