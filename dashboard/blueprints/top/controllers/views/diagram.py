"""Define diagram views."""

from flask import Blueprint, render_template, request

from dashboard.database import get_db_manager

bp = Blueprint("diagram", __name__)


@bp.route("/workflow_diagram")
def workflow_diagram():
    """Define a reusable workflow diagram given a workflow id."""
    workflow_id = request.args.get("workflow_id")
    manager = get_db_manager()

    if not workflow_id:
        return "TODO"

    workflow_id = int(workflow_id)

    sources = manager.sources.get_all(workflow_id=workflow_id)
    form_exists = manager.form_fields.form_exists(workflow_id=workflow_id)
    steps = {source.Step for source in sources}
    outcomes = manager.outcomes.get_all(workflow_id=workflow_id)

    return render_template(
        "components/workflow_diagram.html",
        sources=sources,
        steps=steps,
        workflow_id=workflow_id,
        form_exists=form_exists,
        outcomes=outcomes,
    )
