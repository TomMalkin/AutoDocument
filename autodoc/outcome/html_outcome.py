"""Outcome for creating HTML Files."""

from jinja2 import Template

from autodoc.file_access import LinuxFileAccess
from autodoc.outcome.download_container import DownloadContainer
from autodoc.outcome.outcome import Outcome
from loguru import logger


class HTMLOutcome(Outcome):
    """HTML Document Outcome."""

    is_combination = False

    def __init__(
        self,
        outcome_details: dict,
        template_uploaded_filename=None,
        download_container: DownloadContainer | None = None,
    ) -> None:
        """
        Initialise the outcome with the template and output locations.

        if download_container is given, then assume the result is downloaded.
        """
        self.outcome_details = outcome_details
        self.rendered_text: str
        self.download_container = download_container

        logger.info(f"Creating HTMLOutcome class with {template_uploaded_filename=}")

        if template_uploaded_filename:
            self.template_file_access = LinuxFileAccess(
                root=".", relative=template_uploaded_filename
            )

        else:
            self.set_template_file_accessor()

        if download_container:
            self.output_file_access = LinuxFileAccess(
                root=str(download_container.download_dir),
                relative=outcome_details["OutputFileLocation"],
            )
        else:
            self.set_output_file_accessor()

        self.template_text = self.template_file_access.get_text()
        self.template = Template(self.template_text)

    def render(self, data: dict) -> None:
        """Render the HTML document using jinja2."""
        self.rendered_text = self.template.render(**data)
        self.output_file_access.render(data=data)

    def save(self) -> None:
        """Save the HTML document using standard write."""
        self.output_file_access.save_text(self.rendered_text)
        if self.download_container:
            self.download_container.add_file(file_path=self.output_file_access.path)
