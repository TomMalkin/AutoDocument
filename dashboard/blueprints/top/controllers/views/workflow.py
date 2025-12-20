"""Define workflow views."""

import os

from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    url_for,
)
from loguru import logger
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from werkzeug.wrappers.response import Response

# from autodoc.workflow import WorkflowRunner
from autodoc.config import DOWNLOAD_DIRECTORY
from autodoc.tasks import process_instance

# from autodoc.outcome.download_container import DownloadContainer
from dashboard.database import get_db_manager

from ...forms import CreateWorkflowForm, get_form

bp = Blueprint("workflow", __name__)


@bp.route("/workflow/<workflow_id>")
def workflow(workflow_id: int) -> str:
    """Render the workflow information page."""
    manager = get_db_manager()

    form_fields = manager.form_fields.get_all(workflow_id=workflow_id)

    instances = manager.workflow_instances.get_all(workflow_id=workflow_id)

    workflow = manager.workflows.get(workflow_id=workflow_id)

    outcome_types = manager.outcome_types.get_all()
    outcome_type_mapping = {}
    for outcome_type in outcome_types:
        outcome_type_mapping[outcome_type.Name] = outcome_type.Id

    source_types = manager.source_types.get_all()
    source_type_mapping = {}
    for source_type in source_types:
        source_type_mapping[source_type.Name] = source_type.Id

    return render_template(
        "top/workflow.html",
        workflow=workflow,
        instances=instances,
        form_fields=form_fields,
        outcome_type_mapping=outcome_type_mapping,
        source_type_mapping=source_type_mapping,
    )


@bp.route("/workflow_delete/<workflow_id>")
def delete_workflow(workflow_id: int) -> Response:
    """Render the workflow information page."""
    manager = get_db_manager()
    manager.workflows.delete(workflow_id=workflow_id)
    manager.commit()
    return redirect(url_for("top.base.index"))


@bp.route("/workflow/add/", methods=["POST"])
def create_workflow_view() -> Response:
    """Create a workflow based on a post."""
    logger.info("Adding workflow")
    form = CreateWorkflowForm()

    if form.validate_on_submit():
        if form.name.data:
            manager = get_db_manager()
            workflow = manager.workflows.add(name=form.name.data)
            manager.commit()
            if workflow:
                return redirect(url_for("top.workflow.workflow", workflow_id=workflow.Id))

    return redirect(url_for("top.base.index"))


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
    manager = get_db_manager()

    # for path 3:
    # url_params = request.values
    url_params = {}
    form = get_form(workflow_id, url_params=url_params, manager=manager)

    if request.method == "GET":
        logger.info("GET request identified")

        if form is None:
            logger.info("No form fields or upload fields identified, skipping form generation")

            instance = manager.workflow_instances.add(workflow_id=workflow_id)
            manager.commit()

            process_instance.send(instance_id=instance.Id, upload_mapping={}, form_data={})

        else:
            logger.info("Form fields and/or upload fields identified, rendering form")
            workflow = manager.workflows.get(workflow_id=workflow_id)
            return render_template(
                "top/workflow_instance.html",
                form=form,
                workflow_id=workflow_id,
                workflow_name=workflow.Name,
            )

    else:  # if request.method == "POST":
        assert form is not None
        logger.info("POST request identified")

        if form.validate_on_submit():
            data = {k: v for k, v in form.data.items() if k not in ["submit", "csrf_token"]}

            name_to_file_mapping = {}  # will be like {"Client Record": "client_record.csv"}
            if form.upload_file_fields:
                logger.info(f"processing uploads: {form.upload_file_fields}")

                for upload_file_field in form.upload_file_fields:  # like "Client Record"
                    logger.info(f"processing field: {upload_file_field}")

                    # save the file
                    file = form[upload_file_field].data
                    filename = secure_filename(file.filename)
                    uploaded_file_path = os.path.join(
                        current_app.config["UPLOAD_DIRECTORY"], filename
                    )
                    file.save(uploaded_file_path)

                    logger.info(f"saving to {uploaded_file_path}")

                    # e.g. "Client Record" -> dashboard/files/client_record.csv
                    name_to_file_mapping[upload_file_field] = uploaded_file_path

            instance = manager.workflow_instances.add(workflow_id=workflow_id)
            manager.commit()

            useable_data = {k: v for k, v in data.items() if not isinstance(v, FileStorage)}
            process_instance.send(
                instance_id=instance.Id,
                upload_mapping=name_to_file_mapping,
                form_data=useable_data,
            )

        else:
            return render_template_string(str(form.errors))

    return redirect(url_for("top.workflow.instance_review", instance_id=instance.Id))


@bp.route("/instance_review/<instance_id>/", methods=["GET"])
def instance_review(instance_id: int) -> Response | str:
    """Return a page that shows the ongoing status of a workflow instance."""
    manager = get_db_manager()

    workflow_instance = manager.workflow_instances.get(instance_id=instance_id)

    return render_template(
        "top/instance_review.html",
        workflow_instance=workflow_instance,
    )


@bp.route("/download/<instance_id>/", methods=["GET"])
def download(instance_id: int):
    """Download the zip file for a given instance Id."""
    manager = get_db_manager()
    instance = manager.workflow_instances.get(instance_id=instance_id)

    if instance.Status == "Complete" and instance.workflow.has_download:
        download_dir = DOWNLOAD_DIRECTORY / str(instance.Id)
        zip_filename = download_dir.name + ".zip"
        zip_path = download_dir.parent / zip_filename
        return send_file(zip_path)


@bp.route("/component/source_table/<instance_id>", methods=["GET"])
def source_table(instance_id: int):
    """Table component of source statuses designed to be polled by the instance review page."""
    manager = get_db_manager()
    instance = manager.workflow_instances.get(instance_id=instance_id)

    source_instances = instance.source_instances

    num_processing = len(
        [
            source_instance
            for source_instance in source_instances
            if source_instance.Status != "Loaded"
        ]
    )

    num_complete = len(source_instances) - num_processing

    logger.info(f"The instance.Status is {instance.Status}")
    if instance.Status in ["Complete", "Failure"]:
        text = render_template(
            "components/sources_status.html",
            num_processing=num_processing,
            num_complete=num_complete,
            instance=instance,
        )
        response = make_response(text)
        response.status_code = 286
        return response

    return render_template(
        "components/sources_status.html",
        num_processing=num_processing,
        num_complete=num_complete,
        instance=instance,
    )


@bp.route("/component/outcome_table/<instance_id>", methods=["GET"])
def outcome_table(instance_id: int):
    """Table component of outcome statuses designed to be polled by the instance review page."""
    manager = get_db_manager()
    instance = manager.workflow_instances.get(instance_id=instance_id)

    outcome_instances = instance.outcome_instances

    num_processing = len(
        [
            outcome_instance
            for outcome_instance in outcome_instances
            if outcome_instance.Status != "Complete"
        ]
    )

    num_complete = len(outcome_instances) - num_processing

    if instance.Status in ["Complete", "Failure"]:
        text = render_template(
            "components/outcomes_status.html",
            num_processing=num_processing,
            num_complete=num_complete,
            has_download=instance.workflow.has_download,
            instance=instance,
        )
        response = make_response(text)
        response.status_code = 286
        return response

    return render_template(
        "components/outcomes_status.html",
        num_processing=num_processing,
        num_complete=num_complete,
        has_download=instance.workflow.has_download,
        instance=instance,
    )
