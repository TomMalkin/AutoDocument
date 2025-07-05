"""Manage SharePoint."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

from dashboard.database import get_db_manager

from .forms import CreateMetaSharePoint

bp = Blueprint("sp", "sp")


@bp.route("/manage")
@login_required
def manage():
    """Manage SharePoint Libraries."""
    form = CreateMetaSharePoint()
    manager = get_db_manager()
    sharepoints = manager.storage_instances.get_all_of_type(storage_type="SharePoint")
    return render_template("meta/sharepoint.html", sharepoint_form=form, sharepoints=sharepoints)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a SharePoint library."""
    manager = get_db_manager()
    form = CreateMetaSharePoint()

    if form.validate_on_submit():
        url = form.url.data
        username = form.microsoft_username.data
        password = form.microsoft_password.data
        library = form.library.data

        storage_type = manager.storage_types.get_by_name(name="SharePoint")
        manager.storage_instances.add(
            storage_type=storage_type,
            url=url,
            remote_path=library,
            username=username,
            password=password,
        )
        manager.commit()

    return redirect(url_for("meta.sp.manage"))


@bp.route("/delete/<storage_instance_id>")
@login_required
def delete(storage_instance_id: int):
    """Remove a SharePoint Library."""
    manager = get_db_manager()
    manager.storage_instances.delete(storage_instance_id=storage_instance_id)
    manager.commit()
    return redirect(url_for("meta.sp.manage"))
