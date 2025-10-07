"""Define Word based outcomes."""

from pathlib import Path
from typing import Optional

from docxtpl import DocxTemplate
from loguru import logger

from autodoc.data.tables import Outcome
from autodoc.outcome.outcome import OutcomeService
from autodoc.storage_service import LinuxStorageService


class WordOutcomeService(OutcomeService):
    """Word Outcome."""

    is_combination = False
    is_file = True

    def __init__(
        self,
        outcome: Outcome,
        download_dir: Optional[Path],
        template_uploaded_filename=None,
    ) -> None:
        """Initialise Word Outcome."""
        self.outcome = outcome

        logger.info(f"Creating WordOutcome class with {template_uploaded_filename=}")

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
        temp_file = self.output_storage_service.temp_file()
        self.document.save(temp_file)
        self.output_storage_service.save_file()
