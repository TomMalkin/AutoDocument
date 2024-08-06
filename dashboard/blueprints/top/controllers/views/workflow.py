"""Define workflow views."""

from pathlib import Path
import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    send_file,
    url_for,
    request,
    current_app,
    render_template_string,
)
from loguru import logger
from werkzeug.utils import secure_filename
from dashboard.database import get_manager
from ...forms import CreateWorkflowForm, get_form
from ...models import (
    get_sources,
    get_outcomes,
    get_instances,
    create_workflow,
    get_source,
    get_form_fields_from_source,
    get_form_fields,
    get_workflow_name,
)
from autodoc import Workflow
from werkzeug.wrappers.response import Response
from autodoc.outcome.download_container import DownloadContainer

bp = Blueprint("workflow", __name__)


@bp.route("/workflow/<workflow_id>")
def workflow(workflow_id: int) -> str:
    """Render the workflow information page."""
    sources = get_sources(workflow_id)
    outcomes = get_outcomes(workflow_id)

    form_fields = get_form_fields(workflow_id)

    instances = get_instances(workflow_id)

    manager = get_manager()

    workflow = Workflow(workflow_id=workflow_id, event_logger=None, manager=manager)

    return render_template(
        "top/workflow.html",
        workflow=workflow,
        sources=sources,
        outcomes=outcomes,
        instances=instances,
        form_fields=form_fields,
    )


@bp.route("/workflow_delete/<workflow_id>")
def delete_workflow(workflow_id: int) -> Response:
    """Render the workflow information page."""
    manager = get_manager()
    manager.delete_workflow(workflow_id=workflow_id)
    return redirect(url_for("top.base.index"))


@bp.route("/workflow/add/", methods=["POST"])
def create_workflow_view() -> Response:
    """Create a workflow based on a post."""
    logger.info("Adding workflow")
    form = CreateWorkflowForm()

    if form.validate_on_submit():
        workflow_id = create_workflow(name=form.name.data)
        return redirect(url_for("top.workflow.workflow", workflow_id=workflow_id))

    return redirect(url_for("top.base.index"))


@bp.route("/source/<source_id>/", methods=["GET"])
def source(source_id: int) -> Response | str:
    """Show details about a source."""
    source_details = get_source(source_id)
    form_details = get_form_fields_from_source(source_id)
    source_id = source_details["SourceId"]

    sql_field_form = None

    return render_template(
        "top/source.html",
        source_details=source_details,
        form_details=form_details,
        sql_field_form=sql_field_form,
        source_id=source_id,
    )


@bp.route("/instance/<workflow_id>/", methods=["GET", "POST"])
def workflow_instance(workflow_id: int) -> Response | str:
    """
    Start a workflow and process it.

    This endpoint can be reached in several different ways and all need to be handled correctly.

    1) This endpoint is reached by an internal link with no url params [GET]
        1.a) if there is no user input required such as uploaded documents or specified
             form fields:

             -> Process Workflow with form_data as None

        1.b) there is user input OR upload fields

            -> Display Form with submit button

    2) This endpoint is reached by a POST request, such as from the form from 1.b

            2.a) Submitted form is valid.

            -> Process Workflow with form_data populated

            2.b) Submitted form is not valid

            -> Rerender the form with an error message

    3) This endpoing is reached by a GET request with url_params
    """
    logger.info(f"Workflow Instance page with {request.method=} and {workflow_id=}")
    manager = get_manager()

    # for path 3:
    # url_params = request.values
    url_params = {}
    form = get_form(workflow_id, url_params=url_params, manager=manager)
    download_container = DownloadContainer(download_dir=current_app.config["DOWNLOAD_DIR"])

    if request.method == "GET":
        logger.info("GET request identified")

        if form is None:
            logger.info("No form fields or upload fields identified, skipping form generation")
            workflow = Workflow(workflow_id=workflow_id, event_logger=None, manager=manager)

            workflow.process(download_container=download_container)

        else:
            logger.info("Form fields and/or upload fields identified, rendering form")
            workflow_name = get_workflow_name(workflow_id)
            return render_template(
                "top/workflow_instance.html",
                form=form,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
            )

    if request.method == "POST":
        assert form is not None
        logger.info("POST request identified")

        if form.validate_on_submit():
            data = {k: v for k, v in form.data.items() if k not in ["submit", "csrf_token"]}
            workflow = Workflow(
                workflow_id=workflow_id, form_data=data, event_logger=None, manager=manager
            )

            name_to_file_mapping = {}  # will be like {"Client Record": "client_record.csv"}
            if form.upload_file_fields:
                logger.info(f"processing uploads: {form.upload_file_fields}")

                for upload_file_field in form.upload_file_fields:  # like "Client Record"
                    logger.info(f"processing field: {upload_file_field}")

                    # save the file
                    file = form[upload_file_field].data
                    filename = secure_filename(file.filename)
                    uploaded_file_path = os.path.join(current_app.config["UPLOAD_DIR"], filename)
                    file.save(uploaded_file_path)

                    logger.info(f"saving to {uploaded_file_path}")

                    # e.g. "Client Record" -> dashboard/files/client_record.csv
                    name_to_file_mapping[upload_file_field] = uploaded_file_path

            workflow.process(
                download_container=download_container,
                upload_mapping=name_to_file_mapping,
            )

        else:
            return render_template_string(form.errors)

    # workflow has been completed if we are here
    if download_container.has_files():
        download_container.zip_files()
        zip_path = Path(current_app.config["DOWNLOAD_DIR"]).resolve() / "output.zip"
        logger.info(f"Downloads exist, so zipping to {zip_path=} and sending.")

        return send_file(zip_path)

    return redirect(url_for("top.base.index"))
