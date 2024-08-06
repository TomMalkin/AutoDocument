"""Template for creating other outcomes."""

from abc import ABC, abstractmethod
from autodoc.file_access import FileAccess
from pathlib import Path
from autodoc.file_access.file_details import TemplateFileDetails, OutputFileDetails
from .download_container import DownloadContainer


class Outcome(ABC):
    """Interface for Outcomes."""

    is_combination: bool
    rendered_output_location: str

    input_file_access: FileAccess
    input_path: Path

    output_file_access: FileAccess
    output_path: Path

    is_file: bool

    def __init__(self, outcome_details: dict, download_container: DownloadContainer | None) -> None:
        """
        Initialise the object with a dict of outcome details.

        if download_container is given, then assume the result is downloaded.
        """
        self.outcome_details = outcome_details
        self.download_container = download_container

    def set_template_file_accessor(self):
        """Set the file access for the source if its a file."""
        self.template_file_details = TemplateFileDetails(self.outcome_details)
        self.template_file_access = self.template_file_details.get_file_access_class()
        self.template_path = self.template_file_access.get_file()

    def set_output_file_accessor(self):
        """Set the file access for the source if its a file."""
        self.output_file_details = OutputFileDetails(self.outcome_details)
        self.output_file_access = self.output_file_details.get_file_access_class()

    @abstractmethod
    def render(self, data: dict) -> None:
        """Render the outcome with the given data."""
        raise NotImplementedError()

    @abstractmethod
    def save(self) -> None:
        """Save the rendered outcome."""
        raise NotImplementedError()
