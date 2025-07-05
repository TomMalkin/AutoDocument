"""Define the create workflow form."""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class CreateWorkflowForm(FlaskForm):
    """Create a new Workflow."""

    name = StringField("Name", validators=[InputRequired()])
    submit = SubmitField()
