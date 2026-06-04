"""Define SQL based forms."""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import InputRequired


class CreateDatabaseSourceForm(FlaskForm):
    """Create a Database Source."""

    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])
    field_name = StringField("Field Name")
    is_file = False
    sql_text = TextAreaField("SQL", validators=[InputRequired()])
    database = SelectField("Database", coerce=int)
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()
