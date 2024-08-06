"""Define Meta forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class CreateMetaDatabase(FlaskForm):
    """Create a new Workflow."""

    name = StringField("Name", validators=[InputRequired()])
    connection_string = StringField("Connection String", validators=[InputRequired()])
    submit = SubmitField()
