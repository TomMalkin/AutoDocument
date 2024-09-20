"""Define the ExcelSource and ExcelTable Sources."""

import pandas as pd
from loguru import logger

from autodoc.db import DatabaseManager
from autodoc.file_access.linux import LinuxFileAccess
from autodoc.source.source import Source


class ExcelRecord(Source):
    """
    A Excel file with a single record of data.

    Key values in the source_record is HeaderRow and SheetName.
    """

    is_multi_record = False

    def __init__(
        self, source_details: dict, manager: DatabaseManager, uploaded_filename=None
    ) -> None:
        """Initialise the ExcelRecord with the file_path of the file."""
        logger.info(
            f"loading ExcelRecord class with Source Id {
                source_details['SourceId']} and {uploaded_filename=}"
        )

        self.source_details = source_details
        self.data: dict = {}

        if uploaded_filename:
            self.file_access = LinuxFileAccess(root=".", relative=uploaded_filename)
            self.path = self.file_access.get_file()

        else:
            self.set_file_accessor()

        self.header_row = source_details["HeaderRow"]
        self.sheet_name = source_details["SheetName"]

    def load_data(self, current_data: dict | None = None) -> None:
        """Load the first record from the dataframe."""
        self.dataframe = pd.read_excel(
            self.path,
            sheet_name=self.sheet_name,
            header=self.header_row - 1,
        )

        self.data = self.dataframe.to_dict("records")[0]


class ExcelTable(Source):
    """
    A multirecord Excel table.

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

        self.header_row = source_details["HeaderRow"]
        self.sheet_name = source_details["SheetName"]

    def load_data(self, current_data: dict) -> None:
        """Load the data to a pandas dataframe and then to records."""
        self.dataframe = pd.read_excel(
            self.path,
            sheet_name=self.sheet_name,
            header=self.header_row - 1,
        )
        self.data = list(self.dataframe.to_dict("records"))
