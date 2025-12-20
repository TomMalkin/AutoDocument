"""Define a factory that can create source forms."""

from typing import Optional

from flask import Blueprint

from autodoc.data.tables import SourceType
from dashboard.database import DatabaseManager

from ...forms import ADD_SOURCE_FORMS

bp = Blueprint("source", __name__)


def create_source_form(
    manager: DatabaseManager, source_type: SourceType, initial_data: Optional[dict] = None
):
    """Create a Form for adding or editting a Source."""
    form_type = ADD_SOURCE_FORMS.get(source_type.Name)

    if not form_type:
        raise ValueError(f"Unknown Source Mapping for {source_type.Name}")

    if initial_data:
        form = form_type(data=initial_data)
    else:
        form = form_type()

    if hasattr(form, "database"):
        database_choices = manager.database_meta_sources.get_all()
        form.database.choices = [(db.Id, db.Name) for db in database_choices]

    if hasattr(form, "llm"):
        llms = manager.llms.get_all()
        llm_choices = [(llm.Id, f"{llm.provider.CommonName}: {llm.ModelName}") for llm in llms]

        form.llm.choices = llm_choices

    return form
