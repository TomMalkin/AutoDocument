"""Define changeable config."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# defaults set to container setup, to minimise the docker-compose file.
DB_PATH = os.getenv("DB_PATH", "/db_data/autodoc.db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
DOWNLOAD_DIRECTORY = Path(os.getenv("DOWNLOAD_DIRECTORY", "/download_dir"))
UPLOAD_DIRECTORY = Path(os.getenv("UPLOAD_DIRECTORY", "/upload_dir"))
