"""Define the CSVRecord and CSVTable Sources."""

import pandas as pd

from autodoc.data.tables import Source
from autodoc.storage_service.linux import LinuxStorageService

from .source import SourceService


class CSVRecordSourceService(SourceService):
    """
    A CSV file with a single record of data.

    Data can be horizontal or vertical, represented by the direction attribute.

    vertical records are transposed using pandas.
    """

    is_multi_record = False

    def __init__(self, source: Source, uploaded_filename=None) -> None:
        """Initialise the CSVRecordSourceService with the file_path of the file."""
        self.source = source
        self.data: dict = {}

        if uploaded_filename:
            self.storage_service = LinuxStorageService(root=".", relative=uploaded_filename)
            self.path = self.storage_service.get_file()

        else:
            self.set_storage_service()

        self.orientation = source.Orientation

    def load_data(self, current_data: dict | None = None) -> None:
        """Load the first record from the dataframe."""
        if self.orientation == "horizontal":
            self.dataframe = pd.read_csv(self.path)
        else:
            self.dataframe = pd.read_csv(self.path, header=None, index_col=0).T

        self.data = self.dataframe.to_dict("records")[0]


class CSVTableSourceService(SourceService):
    """
    A multirecord CSV table.

    This is either for grouping i.e. for tables in a document, or for splitting
    workflows for example a list of order IDs to process.
    """

    is_multi_record = True

    def __init__(self, source: Source, uploaded_filename=None) -> None:
        """
        Create a CSVTable class with the path to the csv.

        Also speficity whether it's a splitter or grouper.
        """
        self.data = []
        self.source = source
        if uploaded_filename:
            self.file_access = LinuxStorageService(root=".", relative=uploaded_filename)
            self.path = self.file_access.get_file()

        else:
            self.set_storage_service()

    def load_data(self, current_data: dict) -> None:
        """Load the data to a pandas dataframe and then to records."""
        self.dataframe = pd.read_csv(self.path)
        self.data = list(self.dataframe.to_dict("records"))
