"""Define the DownloadContainer class."""

import os
import zipfile
from pathlib import Path

from loguru import logger


class DownloadContainer:
    """
    Represent a container of downloadable files.

    Files are added to this container and then zipped together at the end.
    """

    def __init__(self, download_dir: str | Path):
        """Initialise with empty file paths and zip file path."""
        self.file_paths = []
        self.zip_file_path = Path(download_dir) / "output.zip"
        self.download_dir = Path(download_dir)

        logger.info(f"init DownloadContainer with {download_dir=} meaning: {self.zip_file_path=}")

    def add_file(self, file_path):
        """Add a path to the file_paths list."""
        self.file_paths.append(file_path)

        logger.debug(f"adding to download container {file_path=}")

    def has_files(self):
        """Return if there are files to be downloaded at the end of the workflow."""
        return bool(self.file_paths)

    def zip_files(self):
        """Combine all files into a zip file."""
        if self.file_paths:
            with zipfile.ZipFile(self.zip_file_path, "w") as zipf:
                for file_path in self.file_paths:
                    zipf.write(file_path, os.path.basename(file_path))
            logger.debug(
                f"Combining all files from the container into a zip file, {self.zip_file_path=}"
            )
        else:
            logger.warning("No files to zip. Skipping zipping process.")
