"""Define Form Field Forms."""

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import InputRequired


class CreateFormFieldForm(FlaskForm):
    """Create a form field."""

    name = StringField("Name of Field", validators=[InputRequired()])
    label = StringField("Label of Field", validators=[InputRequired()])
    choices = [("Integer", "Integer"), ("String", "String")]
    field_type = SelectField("Data Type of Field", choices=choices, validators=[InputRequired()])
    submit = SubmitField()
