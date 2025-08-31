"""Create a base class for sources."""

from abc import ABC, abstractmethod

from autodoc.data.tables import Source
from autodoc.storage_service import get_storage_service


class SourceService(ABC):
    """Base Interface for a Source object."""

    # data: dict | list
    # is_multi_record: bool
    # storage_service: StorageService | None
    # path: Path

    def __init__(self, source: Source, uploaded_filenane=None) -> None:
        """Initialise the object wih a Source object."""
        self.source = source

    def set_storage_service(self):
        """Set the storage service."""
        template = self.source.file_template
        if not template or template.is_download:
            return

        self.storage_service = get_storage_service(file_template=template)

        if self.storage_service:
            self.path = self.storage_service.get_file()

    @abstractmethod
    def load_data(self, current_data: dict) -> None:
        """
        Load the data of the source.

        This method is a placeholder to check if it has been overloaded in the child
        class.

        current_data is passed because some Sources require current data to complete,
        for example as params for a SQL Query.
        """
