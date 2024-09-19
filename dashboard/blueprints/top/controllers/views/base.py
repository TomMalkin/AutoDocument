"""Define base views."""

from flask import Blueprint, render_template, request
from dashboard.database import get_manager
from ...forms import CreateWorkflowForm

bp = Blueprint("base", __name__)


@bp.route("/")
def index() -> str:
    """Render the index page."""
    manager = get_manager()
    workflows = manager.get_workflows()
    form = CreateWorkflowForm()
    return render_template("top/index.html", workflows=workflows, form=form)
