"""Define changeable config."""

import os
from dotenv import load_dotenv

load_dotenv()


INIT_DB_PATH = os.getenv("INIT_DB_PATH", "/app/init/initial_database.db")
TARGET_DB_PATH = os.getenv("TARGET_DB_PATH", "/app/database/autodoc.db")
