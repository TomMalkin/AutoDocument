"""Create a base class for sources."""

from abc import ABC, abstractmethod
from pathlib import Path
from autodoc.file_access import FileAccess
from autodoc.file_access.file_details import SourceFileDetails


class Source(ABC):
    """Base Interface for a Source object."""

    data: dict | list
    is_multi_record: bool
    file_access: FileAccess | None
    path: Path

    def __init__(self, source_details: dict) -> None:
        """Initialise the object wih a dict of source details."""
        self.source_details = source_details

    def set_file_accessor(self):
        """Set the file access for the source if its a file."""
        self.file_details = SourceFileDetails(self.source_details)
        self.file_access = self.file_details.get_file_access_class()
        self.path = self.file_access.get_file()

    @abstractmethod
    def load_data(self, current_data: dict) -> None:
        """
        Load the data of the source.

        This method is a placeholder to check if it has been overloaded in the child
        class.

        current_data is passed because some Sources require current data to complete,
        for example as params for a SQL Query.
        """
