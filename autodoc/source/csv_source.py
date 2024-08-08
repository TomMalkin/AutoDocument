"""Define the CSVRecord and CSVTable Sources."""

import pandas as pd
from loguru import logger

from autodoc.db import DatabaseManager
from autodoc.file_access.linux import LinuxFileAccess
from autodoc.source.source import Source


class CSVRecord(Source):
    """
    A CSV with a single record of data.

    Data can be horizontal or vertical, represented by the direction attribute.

    vertical records are transposed using pandas.
    """

    is_multi_record = False

    def __init__(
        self, source_details: dict, manager: DatabaseManager, uploaded_filename=None
    ) -> None:
        """Initialise the CSVRecord with the file_path of the file."""
        logger.info(
            f"loading CSVRecord class with Source Id {source_details['SourceId']} and {uploaded_filename=}"
        )

        self.source_details = source_details
        self.data: dict = {}

        if uploaded_filename:
            self.file_access = LinuxFileAccess(root=".", relative=uploaded_filename)
            self.path = self.file_access.get_file()

        else:
            self.set_file_accessor()

        self.orientation = source_details["Orientation"]

    def load_data(self, current_data: dict | None = None) -> None:
        """Load the first record from the dataframe."""
        if self.orientation == "horizontal":
            self.dataframe = pd.read_csv(self.path)
        else:
            self.dataframe = pd.read_csv(self.path, header=None, index_col=0).T

        self.data = self.dataframe.to_dict("records")[0]


class CSVTable(Source):
    """
    A multirecord CSV table.

    This is either for grouping i.e. for tables in a document, or for splitting
    workflows for example a list of order IDs to process.
    """

    is_multi_record = True

    def __init__(
        self, source_details: dict, manager: DatabaseManager, uploaded_filename=None
    ) -> None:
        """
        Create a CSVTable class with the path to the csv.

        Also speficity whether it's a splitter or grouper.
        """
        self.data = []
        self.source_details = source_details
        if uploaded_filename:
            self.file_access = LinuxFileAccess(root=".", relative=uploaded_filename)
            self.path = self.file_access.get_file()

        else:
            self.set_file_accessor()

    def load_data(self, current_data: dict) -> None:
        """Load the data to a pandas dataframe and then to records."""
        self.dataframe = pd.read_csv(self.path)
        self.data = list(self.dataframe.to_dict("records"))
