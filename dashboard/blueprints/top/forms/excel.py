"""Define CSV forms."""

from .mixins import FileAccessorMixin
from flask_wtf import FlaskForm
from wtforms import IntegerField  # type: ignore
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import InputRequired  # type: ignore


class CreateExcelRecordSourceForm(FlaskForm, FileAccessorMixin):
    """Create a Record Source."""

    header_row = IntegerField("Header Row", validators=[InputRequired()], default=1)
    sheet_name = StringField("Sheet Name", validators=[InputRequired()], default="Sheet1")
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()

class CreateExcelTableSourceForm(FlaskForm, FileAccessorMixin):
    """Create a CSV Table Form."""

    header_row = IntegerField("Header Row", validators=[InputRequired()], default=1)
    sheet_name = StringField("Sheet Name", validators=[InputRequired()], default="Sheet1")
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])
    field_name = StringField("Field Name")
    submit = SubmitField()

