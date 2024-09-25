from flask import Blueprint, render_template, redirect, url_for
from dashboard.database import get_manager
from typing import Union
from werkzeug.wrappers.response import Response
from flask_login import login_required

from .forms import (
    CreateMetaS3,
)

bp = Blueprint("s3", "s3")


@bp.route("/manage")
@login_required
def manage():
    """Manage S3 Object Storage."""
    form = CreateMetaS3()
    manager = get_manager()
    s3s = manager.get_s3_filesystems().data
    return render_template("meta/s3.html", s3_form=form, s3s=s3s)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a S3 Object Storage."""
    manager = get_manager()
    form = CreateMetaS3()

    if form.validate_on_submit():
        print("validated")
        url = form.url.data
        username = form.s3_username.data
        password = form.s3_password.data
        manager.add_s3(url=url, username=username, password=password)

    print(form.errors)
    return redirect(url_for("meta.s3.manage"))


@bp.route("/delete/<file_access_id>")
@login_required
def delete(file_access_id: int):
    """Remove a S3 Object Storage."""
    manager = get_manager()
    manager.remove_file_access(file_access_id=file_access_id)
    return redirect(url_for("meta.s3.manage"))
