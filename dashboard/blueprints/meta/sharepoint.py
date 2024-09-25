from flask import Blueprint, render_template, redirect, url_for
from dashboard.database import get_manager
from typing import Union
from werkzeug.wrappers.response import Response
from flask_login import login_required

from .forms import (
    CreateMetaSharePoint,
)

bp = Blueprint("sp", "sp")


@bp.route("/manage")
@login_required
def manage():
    """Manage SharePoint Libraries."""
    form = CreateMetaSharePoint()
    manager = get_manager()
    sharepoints = manager.get_sharepoints().data
    return render_template("meta/sharepoint.html", sharepoint_form=form, sharepoints=sharepoints)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a SharePoint library."""
    manager = get_manager()
    form = CreateMetaSharePoint()

    if form.validate_on_submit():
        url = form.url.data
        username = form.microsoft_username.data
        password = form.microsoft_password.data
        library = form.library.data
        manager.add_sharepoint(url=url, username=username, password=password, library=library)

    return redirect(url_for("meta.sp.manage"))


@bp.route("/delete/<file_access_id>")
@login_required
def delete(file_access_id: int):
    """Remove a SharePoint Library."""
    manager = get_manager()
    manager.remove_file_access(file_access_id=file_access_id)
    return redirect(url_for("meta.sp.manage"))
