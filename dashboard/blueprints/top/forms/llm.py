"""Define LLM forms."""

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired


class CreateLLMSourceForm(FlaskForm):
    """Create a Record Source."""

    llm = SelectField(
        "LLM",
        render_kw={
            "hx-get": "/snippet/get_system_prompt",
            "hx-trigger": "change",
            "hx-target": "#system_prompt",
            "hx-swap": "none",
            "hx-vals": "js:{'llm_id': this.value}",
            "hx-on::after-request": "document.getElementById('system_prompt').placeholder = event.detail.xhr.responseText",
        },
    )

    prompt_template = TextAreaField("Prompt Template")
    system_prompt = TextAreaField("System Prompt Override")
    field_name = StringField("Field Name")

    step = IntegerField("Step", validators=[InputRequired()], default=1)
    submit = SubmitField()
