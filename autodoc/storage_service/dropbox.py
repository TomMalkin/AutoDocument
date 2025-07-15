"""Dropbox File Access."""

import tempfile
from pathlib import Path

import dropbox
from dropbox.files import WriteMode
from jinja2 import Template
from loguru import logger

from .base import StorageService


class DropboxStorageService(StorageService):
    """Accessing files on Dropbox."""

    def __init__(self, root, relative, access_token):
        """Initialise with the Dropbox folder path and file path."""
        self.access_token = access_token
        self.folder_path = root
        self.filename_raw = relative
        self.temp_file_name: str = ""

        logger.info(
            f"""Initializing DropboxFileAccess with folder: {root},
            relative path: {relative}, access_token: {access_token}"""
        )

        self.client = dropbox.Dropbox(self.access_token)
        self.filename = ""

    def get_file(self) -> Path:
        """Get a file, return a path that can be used in an open() function."""
        temp_file_name = self._download_file()
        return Path(temp_file_name)

    def get_text(self) -> str:
        """Get the text content of a file."""
        temp_file_name = self._download_file()
        with open(temp_file_name, "r") as f:
            text = f.read()
        return text

    def save_text(self, text) -> None:
        """Save some text to storage."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

            with open(temp_file_name, "w") as f:
                f.write(text)

            self._upload_file(temp_file_name)

    def save_file(self):
        """Save the temporary file to storage."""
        if not self.temp_file_name:
            return

        self._upload_file(self.temp_file_name)

    def _download_file(self) -> str:
        """Download a file to a temp location."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            path = f"{self.folder_path}/{self.filename_raw}"
            logger.info(f"Downloading file from Dropbox: {path}")

            _, res = self.client.files_download(path)
            with open(temp_file_name, "wb") as f:
                f.write(res.content)

        return temp_file_name

    def _upload_file(self, local_path) -> None:
        """Upload a file to Dropbox."""
        path = f"{self.folder_path}/{self.filename}"
        logger.info(f"Uploading file to Dropbox: {path}")

        with open(local_path, "rb") as f:
            self.client.files_upload(f.read(), path, mode=WriteMode.overwrite)

    def render(self, data: dict):
        """Render the appropriate fields in this class with the finalized data."""
        self.filename = Template(self.filename_raw).render(**data)
