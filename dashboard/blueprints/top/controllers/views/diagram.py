"""Define base views."""

from flask import Blueprint, render_template, request
from dashboard.database import get_manager

bp = Blueprint("diagram", __name__)


@bp.route("/workflow_diagram")
def workflow_diagram():
    """Define a reusable workflow diagram given a workflow id."""
    workflow_id = request.args.get("workflow_id")
    sql = """
        select Step step, Id source_id, Splitter splitter
        from Source
        where WorkflowId = :workflow_id
        and Source.TypeId != 4
    """
    params = {"workflow_id": workflow_id}
    manager = get_manager()
    sources = manager.db.recordset(sql=sql, params=params).data

    sql = """
        select sff.Id
        from SourceFormField sff
        join Source s on sff.SourceId = s.Id
        where s.WorkflowId = :workflow_id
    """
    form_exists = bool(manager.db.recordset(sql=sql, params=params).data)

    steps = {x["step"] for x in sources}


    sql = """
        select *
        from vOutcome
        where WorkflowId = :workflow_id
    """

    outcomes = manager.db.recordset(sql=sql, params=params).data

    return render_template(
        "components/workflow_diagram.html",
        sources=sources,
        steps=steps,
        workflow_id=workflow_id,
        form_exists=form_exists,
        outcomes=outcomes,
    )
