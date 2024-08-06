"""Define the template for file access classes."""

from abc import ABC, abstractmethod
from pathlib import Path
import tempfile
import os
from loguru import logger


class FileAccess(ABC):
    """
    FileAccess template for getting and saving files.

    The temp_file_name is used for when remote storage is used like s3. The file
    is downloaded and saved to a tempfile (if a file) or just read and the text
    returned (if a text file).
    """

    @abstractmethod
    def __init__(self, root: str, relative: str, url=None, username=None, password=None):
        """
        Initialise.

            root: the base of the storage location, like the bucket or root path.
            relative: the relative location of the path given the root.
            url: the url of some storage options
            username: username or access key
            password: password or secret key
        """
        self.temp_file_name: str

    @abstractmethod
    def get_file(self) -> Path:
        """Get a file, return a path that can be used in an open() function."""

    @abstractmethod
    def get_text(self) -> str:
        """Get just the text contents of a file."""

    @abstractmethod
    def save_text(self, text) -> None:
        """Save a text to storage."""

    @abstractmethod
    def save_file(self):
        """Save the temporary file to storage."""

    @abstractmethod
    def render(self, data: dict):
        """Render the appropriate fields in this class with the finalised data."""

    def temp_file(self):
        """Set and return a temp_file that can be saved to by outcomes that save files."""
        if not self.temp_file_name:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self.temp_file_name = temp_file.name
                logger.info(f"setting {self.temp_file_name=}")

        return self.temp_file_name

    def clean(self):
        """Remove any temporary files."""
        if self.temp_file_name:
            os.remove(self.temp_file_name)
