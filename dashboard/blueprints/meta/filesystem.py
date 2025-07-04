from flask import Blueprint, render_template, redirect, url_for
from dashboard.database import get_db_manager
from typing import Union
from werkzeug.wrappers.response import Response
from flask_login import login_required

from .forms import (
    CreateMetaFileSystem,
    CreateMetaWindowsFileSystem,
)
from typing import cast

bp = Blueprint("fs", "fs")


@bp.route("/manage")
@login_required
def manage():
    """Manage Windows and Posix file systems."""
    manager = get_db_manager()
    windows_filesystems = manager.storage_instances.get_all_of_type(storage_type="Windows Share")
    windows_filesystem_form = CreateMetaWindowsFileSystem()
    linux_filesystems = manager.storage_instances.get_all_of_type(storage_type="Linux Share")
    linux_filesystem_form = CreateMetaFileSystem()
    return render_template(
        "meta/file_system.html",
        windows_filesystems=windows_filesystems,
        windows_form=windows_filesystem_form,
        linux_filesystems=linux_filesystems,
        linux_form=linux_filesystem_form,
    )


@bp.route("/add_linux", methods=["POST"])
@login_required
def add_linux() -> Union[str, Response]:
    """Add a linux filesystem."""
    manager = get_db_manager()
    form = CreateMetaFileSystem()

    if form.validate_on_submit():
        local_path = cast(str, form.local_path.data).rstrip("/") + "/"
        remote_path = cast(str, form.remote_path.data).rstrip("/") + "/"
        manager.storage_service.add_instance_with_type(
            storage_type_name="Linux Share", local_path=local_path, remote_path=remote_path
        )
        manager.commit()

    return redirect(url_for("meta.fs.manage"))


@bp.route("/add_windows", methods=["POST"])
def add_windows() -> Union[str, Response]:
    """Add a windows filesystem."""
    manager = get_db_manager()
    form = CreateMetaWindowsFileSystem()

    if form.validate_on_submit():
        local_path = cast(str, form.local_path.data).rstrip("/") + "/"
        remote_path = cast(str, form.remote_path.data).rstrip("\\") + "\\"
        manager.storage_service.add_instance_with_type(
            storage_type_name="Windows Share", local_path=local_path, remote_path=remote_path
        )
        manager.commit()

    return redirect(url_for("meta.fs.manage"))


@bp.route("/delete/<int:storage_instance_id>")
@login_required
def delete(storage_instance_id: int):
    """Endpoint to remove a filesystem."""
    manager = get_db_manager()
    manager.storage_instances.delete(storage_instance_id=storage_instance_id)
    manager.commit()
    return redirect(url_for("meta.fs.manage"))
