"""Define Form Field Forms."""

from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired


from flask_wtf import FlaskForm


class CreateFormFieldForm(FlaskForm):
    """Create a form field."""

    name = StringField("Name of Field", validators=[InputRequired()])
    label = StringField("Label of Field")
    choices = [("Integer", "Integer"), ("String", "String")]
    field_type = SelectField("Data Type of Field", choices=choices, validators=[InputRequired()])
    submit = SubmitField()
