"""Outcome for creating PDF Files."""

import subprocess
from pathlib import Path
from typing import Optional

from docxtpl import DocxTemplate
from loguru import logger

from autodoc.data.tables import Outcome
from autodoc.outcome.outcome import OutcomeService
from autodoc.storage_service import LinuxStorageService


class PDFOutcomeService(OutcomeService):
    """
    PDF Outcome.

    Based almost completely on the Word Outcome, but at the end uses
    libreoffice to convert to pdf.
    """

    is_combination = False

    def __init__(
        self,
        outcome: Outcome,
        download_dir: Optional[Path],
        template_uploaded_filename=None,
    ) -> None:
        """Initialise Word Outcome."""
        self.outcome = outcome

        logger.info(f"Creating PDFOutcomeService class with {template_uploaded_filename=}")

        if template_uploaded_filename:
            self.input_storage_service = LinuxStorageService(
                root=".", relative=template_uploaded_filename
            )

        else:
            self.set_input_storage_service()

        if outcome.is_download:
            logger.info("using a download storage service.")

            self.output_storage_service = LinuxStorageService(
                root=str(download_dir),
                relative=outcome.DownloadName,
            )
        else:
            self.set_output_storage_service()

        self.document = DocxTemplate(self.input_storage_service.get_file())

    def render(self, data: dict) -> None:
        """Render the given data to the document."""
        self.document.render(data)
        self.output_storage_service.render(data=data)

    def save(self) -> None:
        """Save the document."""
        temp_file = self.output_storage_service.temp_file()  # docx file
        logger.info(f"the temp file is {temp_file}")

        self.document.save(temp_file)  # docx file

        temp_file_parent = str(Path(temp_file).parent)

        command = [
            "libreoffice",
            "--headless",
            "--infilter='MS Word 2007 XML'",
            "--convert-to",
            "pdf",
            temp_file,
            "--outdir",
            temp_file_parent,
        ]
        logger.info(f"running headless libreoffice command: {command}")

        subprocess.run(command)
        self.output_storage_service.temp_file_name += ".pdf"
        self.output_storage_service.save_file()
