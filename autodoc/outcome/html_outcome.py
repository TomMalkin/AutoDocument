"""Outcome for creating HTML Files."""

from typing import Optional

from jinja2 import Template
from loguru import logger

from autodoc.data.tables import Outcome
from autodoc.outcome.download_container import DownloadContainer
from autodoc.outcome.outcome import OutcomeService
from autodoc.storage_service import LinuxStorageService


class HTMLOutcomeService(OutcomeService):
    """HTML Document Outcome Service."""

    is_combination = False

    def __init__(
        self,
        outcome: Outcome,
        template_uploaded_filename: Optional[str] = None,
        download_container: Optional[DownloadContainer] = None,
    ) -> None:
        """
        Initialise the outcome with the template and output locations.

        if download_container is given, then assume the result is downloaded.
        """
        self.outcome = outcome
        self.rendered_text: str
        self.download_container = download_container

        logger.info(f"Creating HTMLOutcomeService class with {template_uploaded_filename=}")

        if template_uploaded_filename:
            self.input_storage_service = LinuxStorageService(
                root=".", relative=template_uploaded_filename
            )

        else:
            self.set_input_storage_service()

        if download_container and outcome.is_download:
            self.output_storage_service = LinuxStorageService(
                root=str(download_container.download_dir),
                relative=outcome.DownloadName,
            )
        else:
            self.set_output_storage_service()

        self.template = Template(self.input_storage_service.get_text())

    def render(self, data: dict) -> None:
        """Render the HTML document using jinja2."""
        self.rendered_text = self.template.render(**data)
        if self.output_storage_service:
            self.output_storage_service.render(data=data)

    def save(self) -> None:
        """Save the HTML document using standard write."""
        if self.output_storage_service:
            self.output_storage_service.save_text(self.rendered_text)
            if self.download_container:
                self.download_container.add_file(file_path=self.output_storage_service.path)
