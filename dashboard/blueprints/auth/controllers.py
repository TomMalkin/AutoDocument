"""Define Authentication views."""

from flask import Blueprint, request, flash, render_template, redirect, url_for, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user
from loguru import logger

login_manager = LoginManager()

auth_blueprint = Blueprint("auth", "auth_blueprint", url_prefix="/auth")


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Login view."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        logger.info(f"attempting login with {username=} and {password=}")

        if username == "admin" and password == current_app.config["ADMIN_PASSWORD"]:
            logger.info(
                f"login successful against admin password {current_app.config['ADMIN_PASSWORD']}"
            )
            login_user(User("admin"))
            return redirect(url_for("top.base.index"))
        else:
            logger.info(
                f"login wasn't successfull against admin password {
                    current_app.config['ADMIN_PASSWORD']}"
            )
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_blueprint.route("/logout")
def logout():
    """Logout view."""
    logout_user()
    return redirect(url_for("top.base.index"))
