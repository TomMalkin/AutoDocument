"""Define the SharePoint compatiable file access class."""

import tempfile
from pathlib import Path

from jinja2 import Template
from loguru import logger
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

from .base import StorageService


class SharePointSiteStorageService(StorageService):
    """Accessing files on Microsoft SharePoint."""

    def __init__(self, root, relative, url, username, password):
        """
        Initialise with the root and relative paths.

        root: Name of the library i.e. Documents
        url: sharepoint url + site e.g. https://malkinautomation.sharepoint.com/sites/MySite
        relative: the file within that library: /templates/Template.docx
        username + password: for UserContext
        """
        self.url = url
        self.library = root
        self.relative_file_path = relative

        logger.info(
            "Initializing SharePointSiteFileAccess with root: {}, relative: {}, url: {}, username: {}, password: {}".format(
                root, relative, url, username, password
            )
        )

        user_credentials = UserCredential(user_name=username, password=password)
        self.ctx = ClientContext(url).with_credentials(user_credentials)  # type: ignore

        logger.info("request context created")

        self.filename = ""
        self.temp_file_name = ""

    def render(self, data: dict):
        """Render the appropriate fields in this class with the finalised data."""
        self.filename = Template(self.relative_file_path).render(**data)
        logger.info("Rendering the filename to {self.filename=}")

    def get_file(self) -> Path:
        """Get a file, return a path that can be used in an open() function."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

        relative_file_url = str(Path(self.library) / self.relative_file_path)
        logger.info(f"{relative_file_url=}")

        with open(temp_file_name, "wb") as local_file:
            (
                self.ctx.web.get_file_by_server_relative_path(relative_file_url)
                .download(local_file)
                .execute_query()
            )
            logger.info(f"file has been downloaded into: {temp_file_name}")

        return Path(temp_file_name)

    def get_text(self) -> str:
        """Get the text content of a file."""
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

            relative_file_url = str(Path(self.library) / self.relative_file_path)
            with open(temp_file_name, "wb") as local_file:
                (
                    self.ctx.web.get_file_by_server_relative_path(relative_file_url)
                    .download(local_file)
                    .execute_query()
                )
                logger.info(f"file has been downloaded into: {temp_file_name}")

            with open(temp_file_name, "r") as f:
                text = f.read()

        return text

    def ensure_dir(self):
        """Ensure the directory structure exists for file path: path."""
        logger.info("Ensuring directory structure exists")

        full_path = Path(self.library) / Path(self.relative_file_path)

        parent_path = str(full_path.parent)
        logger.info(f"Ensuring the {parent_path=}")
        _ = (
            self.ctx.web.ensure_folder_path(parent_path)
            .get()
            .select(["ServerRelativePath"])
            .execute_query()
        )
        return parent_path

    def save_text(self, text) -> None:
        """Save some text to storage. Must render first."""
        if not self.filename:
            logger.warning("Make sure render is called first.")
            return

        logger.info(f"rendered filename is {self.filename}")

        parent_path = self.ensure_dir()

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file_name = temp_file.name
            logger.info(f"Temporary file created: {temp_file_name}")

            with open(temp_file_name, "w") as f:
                f.write(text)

            with open(temp_file_name, "rb") as file_content:
                folder = self.ctx.web.get_folder_by_server_relative_url(parent_path)
                file_name = Path(self.filename).name
                logger.info(f"{file_name=}")
                file = folder.files.upload(file_content, file_name=file_name).execute_query()
                logger.info(f"File uploaded into: {file.serverRelativeUrl}")

    def save_file(self) -> None:
        """Save a file to storage."""
        if not self.temp_file_name or not self.filename:
            logger.warning("Make sure render is called first.")
            return

        logger.info(f"saving {self.temp_file_name=} to {self.filename=}")

        parent_path = self.ensure_dir()

        with open(self.temp_file_name, "rb") as file_content:
            folder = self.ctx.web.get_folder_by_server_relative_url(parent_path)
            file_name = Path(self.filename).name
            logger.info(f"{file_name=}")
            file = folder.files.upload(file_content, file_name=file_name).execute_query()
            logger.info(f"File uploaded into: {file.serverRelativeUrl}")
