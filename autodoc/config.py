"""Define changeable config."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


DB_PATH = os.getenv("DB_PATH", "/app/database/autodoc.db")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DOWNLOAD_DIRECTORY = Path(os.getenv("DOWNLOAD_DIRECTORY", "/download_dir"))
UPLOAD_DIRECTORY = Path(os.getenv("UPLOAD_DIRECTORY", "/upload_dir"))

