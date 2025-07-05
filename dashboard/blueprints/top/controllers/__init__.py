"""Combine controllers."""

from flask import Blueprint

from .views.base import bp as base_bp
from .views.csv import bp as csv_bp
from .views.diagram import bp as diagram_bp
from .views.excel import bp as excel_bp
from .views.form_field import bp as form_bp
from .views.html import bp as html_bp
from .views.outcome import bp as outcome_bp
from .views.pdf import bp as pdf_bp
from .views.snippet import bp as snippet_bp
from .views.source import bp as source_bp
from .views.sql import bp as sql_bp
from .views.word import bp as word_bp
from .views.workflow import bp as workflow_bp

top_blueprint = Blueprint("top", "top_blueprint")

top_blueprint.register_blueprint(base_bp)
top_blueprint.register_blueprint(workflow_bp)
top_blueprint.register_blueprint(sql_bp)
top_blueprint.register_blueprint(form_bp)
top_blueprint.register_blueprint(csv_bp)
top_blueprint.register_blueprint(snippet_bp)
top_blueprint.register_blueprint(html_bp)
top_blueprint.register_blueprint(word_bp)
top_blueprint.register_blueprint(pdf_bp)
top_blueprint.register_blueprint(source_bp)
top_blueprint.register_blueprint(outcome_bp)
top_blueprint.register_blueprint(diagram_bp)
top_blueprint.register_blueprint(excel_bp)
