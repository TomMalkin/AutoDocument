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


class SQLMixin:
    """Common SQL Fields."""

    is_file = False
    sql_text = TextAreaField("SQL", validators=[InputRequired()])
    database = SelectField("Database", coerce=int)
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()


class CreateRecordSourceForm(FlaskForm, SQLMixin):
    """Create a Record Source."""


class CreateRecordSetSourceForm(FlaskForm, SQLMixin):
    """Create a Record Set Source."""

    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])

    field_name = StringField("Field Name")


class CreateRecordSetTransposeSourceForm(FlaskForm, SQLMixin):
    """Create a Record Set Source."""

    # splitter = BooleanField("Splitter")
    key_field = StringField("Key Field")
    value_field = StringField("Value Field")
