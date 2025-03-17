"""Define workflow views."""

from flask import Blueprint, render_template, request, render_template_string
from dashboard.database import get_manager
from loguru import logger


bp = Blueprint("snippet", __name__)


@bp.route("/snippet/file_accessor_form")
def file_accessor_form_snippet():
    """Return a form snippet based on the type of file access id."""
    file_access_id = request.args.get("option")
    logger.debug(f"Getting file accessor form snippet for {file_access_id=}")

    manager = get_manager()

    if not file_access_id:
        return render_template_string("")

    if file_access_id == "-1":
        snippet_file = "upload.html"
        root_path = None

    else:
        sql = "select * from vFileAccessors where FileAccessId = :file_access_id"
        params = {"file_access_id": int(file_access_id)}

        record = manager.db.record(sql, params).data

        file_access_type_id = record["FileAccessTypeId"]

        snippet_file_map = {
            2: "file_system.html",
            3: "file_system.html",
            4: "s3.html",
            5: "sharepoint.html",
        }

        snippet_file = snippet_file_map.get(file_access_type_id)
        root_path = record["RemotePath"]

    snippet_path = f"top/snippets/{snippet_file}"

    return render_template(snippet_path, root_path=root_path)


@bp.route("/snippet/output_file_accessor_form")
def output_file_accessor_form_snippet():
    """Return a form snippet based on the type of file access id."""
    file_access_id = request.args.get("outputoption")
    placeholder = request.args.get("placeholder")

    manager = get_manager()

    if not file_access_id:
        return render_template_string("")

    if file_access_id == "-1":
        snippet_file = "download.html"
        root_path = None

    else:

        sql = "select * from vFileAccessors where FileAccessId = :file_access_id"
        params = {"file_access_id": int(file_access_id)}

        record = manager.db.record(sql, params).data

        file_access_type_id = record["FileAccessTypeId"]

        snippet_file_map = {
            2: "file_system_output.html",
            3: "file_system_output.html",
            4: "s3_output.html",
            5: "sharepoint_output.html",
        }

        snippet_file = snippet_file_map.get(file_access_type_id)
        root_path = record["RemotePath"]

    if not snippet_file:
        raise

    snippet_path = f"top/snippets/{snippet_file}"

    return render_template(snippet_path, root_path=root_path, placeholder=placeholder)


@bp.route("/snippet/download_preparing", methods=["POST"])
def download_preparing():
    """Return a template that says Download Preparing."""
    return render_template_string("Download Preparing")
