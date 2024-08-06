"""Define the app creation factory."""

from flask import Flask
from .blueprints import bp as top_blueprint
from dotenv import load_dotenv

load_dotenv()

def create_app(template_folder="templates", static_folder="static") -> Flask:
    """Flask app factory."""
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config["SECRET_KEY"] = "any secret string"

    app.register_blueprint(top_blueprint)

    return app
