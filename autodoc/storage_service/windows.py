"""Define the Windows File Access class."""

import shutil
from pathlib import Path, PureWindowsPath

from jinja2 import Template

from .base import StorageService


class WindowsStorageService(StorageService):
    """Accessing files on Windows based file shares."""

    def __init__(self, root, relative, url=None, username=None, password=None):
        """Initialise with the root and relative paths."""
        self.root_path_raw = root
        self.relative_path_raw = relative

        # rendered later
        self.root_path: str
        self.relative_path: str
        self.path: Path

        self.temp_file_name: str = ""

    def render(self, data):
        """Render the relative path of the file."""
        self.relative_path = Template(self.relative_path_raw).render(**data)
        self.root_path = Template(self.root_path_raw).render(**data)
        self.path = Path(self.root_path) / PureWindowsPath(self.relative_path).as_posix()

    def get_raw_file_path(self):
        """Get raw path function."""
        return Path(self.root_path_raw) / PureWindowsPath(self.relative_path_raw).as_posix()

    def get_text(self):
        """
        Get the text of the file.

        If this is called, then we know the raw root and relatives are an actual file because we're
        dealing with an input or templates.
        """
        path = self.get_raw_file_path()
        with open(path, "r") as f:
            return f.read()

    def get_file(self):
        """Get the path of the file."""
        return self.get_raw_file_path()

    def save_text(self, text) -> None:
        """Save a text to storage."""
        with open(self.path, "w") as f:
            f.write(text)

    def save_file(self):
        """Save the temporary file to storage."""
        if not self.temp_file_name:
            return

        shutil.copy(self.temp_file_name, self.path)
