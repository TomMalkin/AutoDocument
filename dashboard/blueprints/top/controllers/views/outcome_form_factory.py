"""Define a factory that can create outcome forms."""

from typing import Optional

from flask import Blueprint

from autodoc.data.tables import OutcomeType
from dashboard.database import DatabaseManager

from ...forms import ADD_OUTCOME_FORMS

bp = Blueprint("outcome_form_factory", __name__)


def create_outcome_form(
    manager: DatabaseManager, outcome_type: OutcomeType, initial_data: Optional[dict] = None
):
    """Create a Form for adding or editing an Outcome."""
    form_type = ADD_OUTCOME_FORMS.get(outcome_type.Name)

    if not form_type:
        raise ValueError(f"Unknown Outcome Mapping for {outcome_type.Name}")

    if initial_data:
        form = form_type(data=initial_data)
    else:
        form = form_type()

    # Populate storage instance choices for both input and output files
    storage_instances = manager.storage_instances.get_all()
    storage_choices = [(-1, "Uploaded during Workflow")] + [
        (si.Id, f"({si.storage_type.Name}) {si.RemotePath or si.URL}") for si in storage_instances
    ]

    if hasattr(form, "option"): # This corresponds to input_file_template
        form.option.choices = storage_choices

    if hasattr(form, "outputoption"): # This corresponds to output_file_template
        form.outputoption.choices = storage_choices

    return form
