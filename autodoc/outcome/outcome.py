"""Template for creating other outcomes."""

from abc import ABC, abstractmethod
from autodoc.storage_service import StorageService, get_storage_service
from pathlib import Path

# from autodoc.file_access.file_details import TemplateFileDetails, OutputFileDetails
from .download_container import DownloadContainer
from autodoc.data.tables import Outcome

class OutcomeService(ABC):
    """Service layer for an Outcome."""

    is_combination: bool
    rendered_output_location: str

    input_storage_service:StorageService
    input_path: Path

    output_storage_service:StorageService
    output_path: Path

    is_file: bool

    def __init__(self, outcome: Outcome, download_container: DownloadContainer | None) -> None:
        """
        Initialise the object with a dict of outcome details.

        if download_container is given, then assume the result is downloaded.
        """
        self.outcome = outcome
        self.download_container = download_container

    def set_input_storage_service(self):
        """Set the input storage service."""
        template = self.outcome.input_file_template
        if not template or template.is_download:
            return

        self.input_storage_service = get_storage_service(file_template=template)

        if self.input_storage_service:
            self.template_path = self.input_storage_service.get_file()

    def set_output_storage_service(self):
        """Set the output storage service."""
        template = self.outcome.output_file_template
        self.output_storage_service = get_storage_service(file_template=template)

        if self.output_storage_service:
            self.template_path = self.output_storage_service.get_file()

    @abstractmethod
    def render(self, data: dict) -> None:
        """Render the outcome with the given data."""
        raise NotImplementedError()

    @abstractmethod
    def save(self) -> None:
        """Save the rendered outcome."""
        raise NotImplementedError()
