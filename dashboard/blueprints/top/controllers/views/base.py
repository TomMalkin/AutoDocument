"""Define base views."""

from flask import Blueprint, render_template
from dashboard.database import get_db_manager
from ...forms import CreateWorkflowForm


bp = Blueprint("base", __name__)


@bp.route("/")
def index() -> str:
    """Render the index page."""
    manager = get_db_manager()
    workflows = manager.workflows.get_all()

    form = CreateWorkflowForm()
    return render_template("top/index.html", workflows=workflows, form=form)
