from flask import Blueprint, render_template, redirect, url_for
from dashboard.database import get_db_manager
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
    manager = get_db_manager()
    s3s = manager.storage_instances.get_all_of_type(storage_type="S3")
    return render_template("meta/s3.html", s3_form=form, s3s=s3s)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a S3 Object Storage."""
    manager = get_db_manager()
    form = CreateMetaS3()

    if form.validate_on_submit():
        print("validated")
        url = form.url.data
        username = form.s3_username.data
        password = form.s3_password.data
        manager.storage_service.add_instance_with_type(
            storage_type_name="S3", url=url, username=username, password=password
        )

    print(form.errors)
    return redirect(url_for("meta.s3.manage"))


@bp.route("/delete/<storage_instance_id>")
@login_required
def delete(storage_instance_id: int):
    """Remove a S3 Object Storage."""
    manager = get_db_manager()
    manager.storage_instances.delete(storage_instance_id=storage_instance_id)
    return redirect(url_for("meta.s3.manage"))
