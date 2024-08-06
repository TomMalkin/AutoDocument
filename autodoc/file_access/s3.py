"""Define the S3 compatiable file access class."""

from jinja2 import Template
import boto3

from .file_access import FileAccess
from pathlib import Path

import tempfile

from loguru import logger


class S3FileAccess(FileAccess):
    """Accessing files on S3 compatible object storage."""

    def __init__(self, root, relative, url, username, password):
        """Initialise with the root and relative paths."""
        self.url = url
        self.access_key = username
        self.secret_key = password
        self.bucket = root
        self.filename_raw = relative

        self.temp_file_name: str = ""

        logger.info(
            "Initializing with root: {}, relative: {}, url: {}, username: {}, password: {}".format(
                root, relative, url, username, password
            )
        )

        self.client = boto3.client(
            "s3",
            endpoint_url=url,
            aws_access_key_id=username,
            aws_secret_access_key=password,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        self.filename = ""

    def get_file(self) -> Path:
        """Get a file, return a path that can be used in an open() function."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

        self.client.download_file(self.bucket, self.filename_raw, temp_file_name)
        logger.info(f"File downloaded from bucket: {self.bucket}, filename: {self.filename_raw}")

        return Path(temp_file_name)

    def get_text(self) -> str:
        """Get the text content of a file."""
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

            self.client.download_file(self.bucket, self.filename_raw, temp_file_name)
            logger.info(
                f"File downloaded from bucket: {self.bucket}, filename: {self.filename_raw}"
            )

            with open(temp_file_name, "r") as f:
                text = f.read()

        return text

    def save_text(self, text) -> None:
        """Save some text to storage."""
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

            with open(temp_file_name, "w") as f:
                f.write(text)

            self.client.upload_file(temp_file_name, self.bucket, self.filename)

    def save_file(self):
        """Save the temporary file to storage."""
        if not self.temp_file_name:
            return

        self.client.upload_file(self.temp_file_name, self.bucket, self.filename)
        logger.info(
            f"uploading file to s3: {self.temp_file_name=}, {self.bucket=}, {self.filename=}"
        )

    def render(self, data: dict):
        """Render the appropriate fields in this class with the finalised data."""
        self.filename = Template(self.filename_raw).render(**data)
