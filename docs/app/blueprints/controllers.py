from flask import Blueprint, render_template

bp = Blueprint("top", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/sources")
def sources():
    return render_template("sources.html")


@bp.route("/outcomes")
def outcomes():
    return render_template("outcomes.html")


@bp.route("/file_storages")
def file_storages():
    return render_template("file_storages.html")


@bp.route("/databases")
def databases():
    return render_template("databases.html")


@bp.route("/templating")
def templating():
    return render_template("templating.html")
