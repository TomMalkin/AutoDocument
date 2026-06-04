"""Define the Excel Source."""

from typing import Optional

import pandas as pd
from loguru import logger

from autodoc.data.tables import Source
from autodoc.storage_service import LinuxStorageService

from .source import SourceService


class ExcelSourceService(SourceService):
    """
    A multirecord Excel table.

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
        self.dataframe = pd.read_excel(
            self.path,
            sheet_name=self.source.SheetName,
            header=self.source.HeaderRow - 1,
        )
        self.data = list(self.dataframe.to_dict("records"))

    def check(self) -> tuple[bool, Optional[str]]:
        """Check if this source can be loaded. Returns (can be loaded, reason why not)."""
        if self.file_exists():
            logger.info(f"File exists, so source can be loaded (path is {self.path})")
            return True, None

        logger.info(f"File does not exist, so source can not be loaded (path is {self.path})")
        return False, f"File does not exist: {self.path}"
