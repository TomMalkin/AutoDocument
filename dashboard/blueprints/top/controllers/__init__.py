"""Combine controllers."""

from flask import Blueprint

from .views.base import bp as base_bp
from .views.diagram import bp as diagram_bp
from .views.form_field import bp as form_bp
from .views.outcome import bp as outcome_bp
from .views.snippet import bp as snippet_bp
from .views.source import bp as source_bp
from .views.workflow import bp as workflow_bp

top_blueprint = Blueprint("top", "top_blueprint")

top_blueprint.register_blueprint(base_bp)
top_blueprint.register_blueprint(workflow_bp)
top_blueprint.register_blueprint(form_bp)
top_blueprint.register_blueprint(snippet_bp)
top_blueprint.register_blueprint(source_bp)
top_blueprint.register_blueprint(outcome_bp)
top_blueprint.register_blueprint(diagram_bp)
