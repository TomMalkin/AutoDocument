"""Define snippet views."""

from flask import Blueprint, render_template, render_template_string, request
from loguru import logger

from dashboard.database import get_db_manager

bp = Blueprint("snippet", __name__)


@bp.route("/snippet/input_storage_instance_form")
def input_storage_instance_form_snippet():
    """Return a form snippet based on the type of storage instance."""
    storage_instance_id_str = request.args.get("option")

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


