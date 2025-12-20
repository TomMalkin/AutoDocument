"""Define the app creation factory."""

import os

import click
from dotenv import load_dotenv
from flask import Flask
from flask.cli import with_appcontext

from autodoc.config import DB_PATH, DOWNLOAD_DIRECTORY, UPLOAD_DIRECTORY
from autodoc.data.initialise import initialise_database
from dashboard.database import register_db_teardown

from .blueprints import auth_blueprint, card_blueprint, meta_blueprint, top_blueprint
from .blueprints.auth.controllers import login_manager

load_dotenv()

# UPLOAD_DIR = Path("dashboard/files/")
# if not UPLOAD_DIR.is_dir():
#     print("creating upload folder: ", UPLOAD_DIR)
#     UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# if not DOWNLOAD_DIRECTORY.is_dir():
#     print("creating upload folder: ", DOWNLOAD_DIRECTORY)
#     DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Initialise the Database."""
    initialise_database(DB_PATH)


def create_app(template_folder="templates", static_folder="static") -> Flask:
    """Flask app factory."""
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config["SECRET_KEY"] = "any secret string"
    # app.config["UPLOAD_DIR"] = UPLOAD_DIR
    app.config["DOWNLOAD_DIRECTORY"] = DOWNLOAD_DIRECTORY
    app.config["UPLOAD_DIRECTORY"] = UPLOAD_DIRECTORY
    app.config["DB_PATH"] = DB_PATH
    app.config["ADMIN_PASSWORD"] = ADMIN_PASSWORD
    app.secret_key = "your_secret_key"

    app.cli.add_command(init_db_command)

    # init_app(app)
    register_db_teardown(app)

    app.register_blueprint(top_blueprint, url_prefix="/")
    app.register_blueprint(meta_blueprint, url_prefix="/meta")
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(card_blueprint)

    login_manager.init_app(app)

    return app
