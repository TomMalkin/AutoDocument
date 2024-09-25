from flask import Blueprint, render_template, redirect, url_for
from dashboard.database import get_manager
from typing import Union
from werkzeug.wrappers.response import Response
from flask_login import login_required

from .forms import (
    CreateMetaFileSystem,
    CreateMetaWindowsFileSystem,
)

bp = Blueprint("fs", "fs")


@bp.route("/manage")
@login_required
def manage():
    """Manage Windows and Posix file systems."""
    manager = get_manager()
    windows_filesystems = manager.get_windows_filesystems().data
    windows_filesystem_form = CreateMetaWindowsFileSystem()
    posix_filesystems = manager.get_posix_filesystems().data
    posix_filesystem_form = CreateMetaFileSystem()
    return render_template(
        "meta/file_system.html",
        windows_filesystems=windows_filesystems,
        windows_form=windows_filesystem_form,
        posix_filesystems=posix_filesystems,
        posix_form=posix_filesystem_form,
    )


@bp.route("/add_posix", methods=["POST"])
@login_required
def add_posix() -> Union[str, Response]:
    """Add a posix filesystem."""
    manager = get_manager()
    form = CreateMetaFileSystem()

    if form.validate_on_submit():
        local_path = form.local_path.data.rstrip("/") + "/"
        remote_path = form.remote_path.data.rstrip("/") + "/"

        manager.add_posix_filesystem(local_path=local_path, remote_path=remote_path)

    return redirect(url_for("meta.fs.manage"))


@bp.route("/add_windows", methods=["POST"])
def add_windows() -> Union[str, Response]:
    """Add a windows filesystem."""
    manager = get_manager()
    form = CreateMetaWindowsFileSystem()

    if form.validate_on_submit():
        local_path = form.local_path.data.rstrip("/") + "/"
        remote_path = form.remote_path.data.rstrip("\\") + "\\"
        manager.add_windows_filesystem(local_path=local_path, remote_path=remote_path)

    return redirect(url_for("meta.fs.manage"))


@bp.route("/delete/<file_access_id>")
@login_required
def delete(file_access_id):
    """Endpoint to remove a filesystem."""
    manager = get_manager()
    manager.remove_file_access(file_access_id)
    return redirect(url_for("meta.fs.manage"))
