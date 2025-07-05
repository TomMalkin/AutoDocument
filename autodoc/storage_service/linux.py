"""Define the linux filesystem based file access."""

import shutil
from pathlib import Path

from jinja2 import Template
from loguru import logger

from .base import StorageService


class LinuxStorageService(StorageService):
    """Accessing files on linux based file shares."""

    def __init__(self, root: str, relative: str, **kwargs):
        """Initialise with the root and relative paths."""
        self.root_path_raw = root
        self.relative_path_raw = relative

        if not self.relative_path_raw:
            raise

        # rendered later
        self.root_path: str
        self.relative_path: str
        self.path: Path

        self.temp_file_name: str = ""

    def render(self, data: dict):
        """
        Render the relative path of the file by substituting fields in the raw path.

        For example if data = {"client_id": 28}:
            "/home/tom/{{ client_id }} - invoice.docx"
            -> "/home/tom/28 - invoice.docx"

        """
        self.relative_path = Template(self.relative_path_raw).render(**data)
        self.root_path = Template(self.root_path_raw).render(**data)
        self.path = Path(self.root_path) / Path(self.relative_path)

    def get_text(self) -> str:
        """
        Get the text of the file.

        If this is called, then we know the raw root and relatives are an actual file because we're
        dealing with an input or templates.
        """
        path = Path(self.root_path_raw) / Path(self.relative_path_raw)
        with open(path, "r") as f:
            return f.read()

    def get_file(self) -> Path:
        """Get the path of the file."""
        return Path(self.root_path_raw) / Path(self.relative_path_raw)

    def save_text(self, text) -> None:
        """Save a text to storage."""
        with open(self.path, "w") as f:
            f.write(text)

    def save_file(self) -> None:
        """Save the temporary file to storage."""
        if not self.temp_file_name:
            return

        shutil.copy(self.temp_file_name, self.path)
        logger.info(f"Saved {self.temp_file_name} to {self.path}")
