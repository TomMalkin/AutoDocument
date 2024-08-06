"""Outcome for creating PDF Files."""

import subprocess
from pathlib import Path
from loguru import logger

from docxtpl import DocxTemplate  # type: ignore

from autodoc.outcome.download_container import DownloadContainer
from autodoc.outcome.outcome import Outcome
from autodoc.file_access import LinuxFileAccess


class PDFOutcome(Outcome):
    """
    PDF Outcome.

    Based almost completely on the Word Outcome, but at the end uses
    libreoffice to convert to pdf.
    """

    is_combination = False

    def __init__(
        self,
        outcome_details: dict,
        template_uploaded_filename=None,
        download_container: DownloadContainer | None = None,
    ) -> None:
        """Initialise Word Outcome."""
        self.outcome_details = outcome_details
        self.download_container = download_container

        logger.info(f"Creating HTMLOutcome class with {template_uploaded_filename=}")

        if template_uploaded_filename:
            self.template_file_access = LinuxFileAccess(
                root=".", relative=template_uploaded_filename
            )

        else:
            self.set_template_file_accessor()

        if download_container:
            self.output_file_access = LinuxFileAccess(
                root=str(download_container.download_dir),
                relative=outcome_details["OutputFileLocation"],
            )
        else:
            self.set_output_file_accessor()

    def render(self, data: dict) -> None:
        """Render the given data to the document."""
        self.document = DocxTemplate(self.template_file_access.get_file())

        self.document.render(data)
        self.output_file_access.render(data=data)

    def save(self) -> None:
        """Save the document."""
        temp_file = self.output_file_access.temp_file()  # final pdf file
        self.document.save(temp_file)  # docx file
        temp_file_parent = Path(temp_file).parent

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
        self.output_file_access.temp_file_name += ".pdf"
        self.output_file_access.save_file()
        if self.download_container:
            self.download_container.add_file(file_path=self.output_file_access.path)
