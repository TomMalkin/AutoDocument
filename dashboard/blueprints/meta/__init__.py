"""
Define the meta blueprint.

Meta refers to persistant user defined configs, such as databases, filesystems, remote storage
credentials etc.
"""

from .controllers import meta_blueprint as meta_blueprint
from .database import bp as database_bp
from .filesystem import bp as filesystem_bp
from .s3 import bp as s3_bp
from .sharepoint import bp as sharepoint_bp

meta_blueprint.register_blueprint(database_bp, url_prefix="/db")
meta_blueprint.register_blueprint(filesystem_bp, url_prefix="/fs")
meta_blueprint.register_blueprint(sharepoint_bp, url_prefix="/sp")
meta_blueprint.register_blueprint(s3_bp, url_prefix="/s3")
