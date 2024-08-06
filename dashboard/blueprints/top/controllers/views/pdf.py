"""Define Microsoft Word views."""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from ...forms import CreatePDFOutcomeForm
from ...models import get_file_accessors, add_pdf_outcome
from werkzeug.wrappers.response import Response
from loguru import logger
from dashboard.database import get_manager

from typing import Union

bp = Blueprint("pdf", __name__)


@bp.route("/workflow/<workflow_id>/add_pdf_outcome", methods=["GET", "POST"])
def add_pdf_outcome_view(workflow_id: int) -> Union[str, Response]:
    """Add a PDF outcome."""
    form = CreatePDFOutcomeForm()

    if form.validate_on_submit():
        location = form.location.data
        bucket = form.bucket.data
        name = form.name.data

        if name:
            sql = "select Name from Source where WorkflowId = :workflow_id"
            params = {"workflow_id": workflow_id}
            current_names = get_manager().db.recordset(sql=sql, params=params).column("Name")

            if name in current_names:
                logger.info(f"attempted add of {name} when existing names are {current_names}")
                flash(f"{name} already exists, choose another name", "error")
                return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

        file_access_id = None

        if request.form["option"]:
            file_access_id = int(request.form["option"])
            if file_access_id == -1:
                file_access_id = None

        output_location = form.output_location.data
        output_bucket = form.output_bucket.data
        output_file_access_id = None

        download_name = form.download_name.data

        if download_name:
            output_location = download_name

        if request.form["outputoption"]:
            output_file_access_id = int(request.form["outputoption"])
            if output_file_access_id == -1:
                output_file_access_id = get_manager().get_download_access_id()

        add_pdf_outcome(
            workflow_id,
            input_file_access_id=file_access_id,
            input_location=location,
            input_bucket=bucket,
            output_file_access_id=output_file_access_id,
            output_location=output_location,
            output_bucket=output_bucket,
            name=name,
        )

        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    file_access_list = get_file_accessors()

    return render_template(
        "top/add_outcome/add_pdf_outcome.html",
        form=form,
        workflow_id=workflow_id,
        file_access_list=file_access_list,
    )
