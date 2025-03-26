"""Define SQL based forms."""

from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    SelectField,
    BooleanField,
    StringField,
    IntegerField,
    SubmitField,
    RadioField,
)
from wtforms.validators import InputRequired


class CreateRecordSourceForm(FlaskForm):
    """Create a Record Source."""

    sql_text = TextAreaField("SQL", validators=[InputRequired()])
    database = SelectField("Database")
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()


class CreateRecordSetSourceForm(FlaskForm):
    """Create a Record Set Source."""

    sql_text = TextAreaField("SQL", validators=[InputRequired()])
    database = SelectField("Database")
    splitter_choice = RadioField(choices=[("splitter", "splitter"), ("field", "field")])

    field_name = StringField("Field Name")
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()


class CreateRecordSetTransposeSourceForm(FlaskForm):
    """Create a Record Set Source."""

    sql_text = TextAreaField("SQL", validators=[InputRequired()])
    database = SelectField("Database")
    splitter = BooleanField("Splitter")
    key_field = StringField("Key Field")
    value_field = StringField("Value Field")
    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()
