"""Define the app creation factory."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from loguru import logger

from autodoc.config import TARGET_DB_PATH
from dashboard.database import register_db_teardown

from .blueprints import auth_blueprint, card_blueprint, meta_blueprint, top_blueprint
from .blueprints.auth.controllers import login_manager

load_dotenv()

logger.remove()
logger.add(sys.stderr, level="INFO")

UPLOAD_DIR = Path("dashboard/files/")
if not UPLOAD_DIR.is_dir():
    print("creating upload folder: ", UPLOAD_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DOWNLOAD_DIR = Path("dashboard/files/download/")
if not DOWNLOAD_DIR.is_dir():
    print("creating upload folder: ", DOWNLOAD_DIR)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

logger.add("log.log")


def create_app(template_folder="templates", static_folder="static") -> Flask:
    """Flask app factory."""
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config["SECRET_KEY"] = "any secret string"
    app.config["UPLOAD_DIR"] = UPLOAD_DIR
    app.config["DOWNLOAD_DIR"] = DOWNLOAD_DIR
    app.config["DB_PATH"] = TARGET_DB_PATH
    app.config["ADMIN_PASSWORD"] = ADMIN_PASSWORD
    app.secret_key = "your_secret_key"

    # init_app(app)
    register_db_teardown(app)

    # initialise_database(initial_db=INIT_DB_PATH, target_db=TARGET_DB_PATH)

    app.register_blueprint(top_blueprint, url_prefix="/")
    app.register_blueprint(meta_blueprint, url_prefix="/meta")
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(card_blueprint)

    login_manager.init_app(app)

    return app
