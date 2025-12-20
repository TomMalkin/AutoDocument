"""Define snippet views."""

from flask import Blueprint, render_template, render_template_string, request
from loguru import logger

from dashboard.database import get_db_manager

bp = Blueprint("snippet", __name__)


@bp.route("/snippet/storage_instance_form")
def storage_instance_form_snippet():
    """
    Return a form snippet based on the type of storage instance.

    This is a generic function that can handle source and outcomes, and also
    input and output file storages.

    Also handles if it is an add or an edit.
    """
    storage_instance_id = request.args.get("option") or request.args.get("outputoption")
    storage_type = request.args.get("storage_type", "input")
    source_id = request.args.get("source_id")
    outcome_id = request.args.get("outcome_id")
    placeholder = request.args.get("placeholder")

    manager = get_db_manager()

    # if the form snippet is an edit rather than an add, then we fill up the context
    # and pass that to the snippet
    context = {"storage_type": storage_type, "placeholder": placeholder}

    if source_id:
        logger.info(f"{source_id=} so Source identified.")
        source = manager.sources.get(source_id=int(source_id))
        context["name"] = source.Name
        if source.file_template:
            context.update(
                {
                    "location": source.file_template.Location,
                    "bucket": source.file_template.Bucket,
                    "name": source.Name,
                }
            )

    elif outcome_id:
        logger.info(f"{outcome_id=} so Outcome identified.")
        outcome = manager.outcomes.get(outcome_id=int(outcome_id))
        if storage_type=="input":
            context["name"] = outcome.Name
        else:
            context["name"] = outcome.DownloadName

        if storage_type == "input" and outcome.input_file_template:
            context.update(
                {
                    "location": outcome.input_file_template.Location,
                    "bucket": outcome.input_file_template.Bucket,
                }
            )
        elif storage_type == "output" and outcome.output_file_template:
            context.update(
                {
                    "location": outcome.output_file_template.Location,
                    "bucket": outcome.output_file_template.Bucket,
                }
            )

    if not storage_instance_id:
        return render_template_string("")

    storage_instance_id = int(storage_instance_id)

    if storage_instance_id == -1:
        if storage_type == "input":
            snippet_file = "upload.html"
        else:  # output
            snippet_file = "download.html"
        root_path = None
    else:
        storage_instance = manager.storage_instances.get(storage_instance_id=storage_instance_id)
        if storage_instance:
            snippet_file_map = {
                "Linux Share": "file_system.html",
                "Windows Share": "file_system.html",
                "S3": "s3.html",
                "SharePoint": "sharepoint.html",
            }
            snippet_file = snippet_file_map.get(storage_instance.storage_type.Name)
            root_path = storage_instance.RemotePath
        else:
            raise ValueError("Storage instance not found")

    snippet_path = f"top/snippets/{snippet_file}"
    return render_template(snippet_path, root_path=root_path, **context)


@bp.route("/snippet/input_storage_instance_form")
def input_storage_instance_form_edit_snippet():
    """Return a form snippet based on the type of storage instance."""
    storage_instance_id_str = request.args.get("option")
    source_id_str = request.args.get("source_id")

    manager = get_db_manager()

    context = {"root_path": None}
    if source_id_str:
        source = manager.sources.get(source_id=int(source_id_str))
        context["name"] = source.Name
        if source.file_template:
            context["location"] = source.file_template.Location
            context["bucket"] = source.file_template.Bucket

    if not storage_instance_id_str:
        return render_template_string("")

    storage_instance_id = int(storage_instance_id_str)

    logger.debug(f"Getting file accessor form edit snippet for {storage_instance_id=}")

    if storage_instance_id == -1:
        snippet_file = "upload.html"

    else:
        storage_instance = manager.storage_instances.get(storage_instance_id=storage_instance_id)
        if not storage_instance:
            raise ValueError("Storage instance not found")

        if storage_instance:
            snippet_file_map = {
                "Linux Share": "file_system.html",
                "Windows Share": "file_system.html",
                "S3": "s3.html",
                "SharePoint": "sharepoint.html",
            }
            snippet_file = snippet_file_map.get(storage_instance.storage_type.Name)
            context["root_path"] = storage_instance.RemotePath

        else:
            raise

    snippet_path = f"top/snippets/{snippet_file}"
    return render_template(snippet_path, **context)


@bp.route("/snippet/output_storage_instance_form")
def output_storage_instance_form_snippet():
    """Return a form snippet based on the type of file access id."""
    storage_instance_id_str = request.args.get("outputoption")
    placeholder = request.args.get("placeholder")

    if not storage_instance_id_str:
        return render_template_string("")

    storage_instance_id = int(storage_instance_id_str)

    logger.debug(f"Getting file accessor form snippet for {storage_instance_id=}")

    manager = get_db_manager()

    if storage_instance_id == -1:
        snippet_file = "download.html"
        root_path = None

    else:
        storage_instance = manager.storage_instances.get(storage_instance_id=storage_instance_id)

        if storage_instance:
            snippet_file_map = {
                "Linux Share": "file_system_output.html",
                "Windows Share": "file_system_output.html",
                "S3": "s3_output.html",
                "SharePoint": "sharepoint_output.html",
            }
            snippet_file = snippet_file_map.get(storage_instance.storage_type.Name)
            root_path = storage_instance.RemotePath

        else:
            raise

    snippet_path = f"top/snippets/{snippet_file}"

    return render_template(snippet_path, root_path=root_path, placeholder=placeholder)


@bp.route("/snippet/download_preparing", methods=["POST"])
def download_preparing():
    """Return a template that says Download Preparing."""
    return render_template_string("Download Preparing")


@bp.route("/snippet/get_system_prompt", methods=["GET"])
def get_system_prompt():
    """Get the default system prompt for a given LLM Id."""
    llm_id = request.values.get("llm")
    manager = get_db_manager()
    llm = manager.llms.get(llm_id=llm_id)
    return llm.SystemPrompt if llm else "Error"


@bp.route("/snippet/input_storage_instance_form")
def input_storage_instance_form_snippet():
    """Return a form snippet based on the type of storage instance."""
    storage_instance_id_str = request.args.get("option")
    source_id_str = request.args.get("source_id")

    if not storage_instance_id_str:
        return render_template_string("")

    storage_instance_id = int(storage_instance_id_str)

    logger.debug(f"Getting file accessor form snippet for {storage_instance_id=}")

    manager = get_db_manager()

    if storage_instance_id == -1:
        snippet_file = "upload.html"
        root_path = None

    else:
        storage_instance = manager.storage_instances.get(storage_instance_id=storage_instance_id)

        if storage_instance:
            snippet_file_map = {
                "Linux Share": "file_system.html",
                "Windows Share": "file_system.html",
                "S3": "s3.html",
                "SharePoint": "sharepoint.html",
            }
            snippet_file = snippet_file_map.get(storage_instance.storage_type.Name)
            root_path = storage_instance.RemotePath

        else:
            raise

    snippet_path = f"top/snippets/{snippet_file}"
    return render_template(snippet_path, root_path=root_path)
