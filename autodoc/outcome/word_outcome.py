"""Define Word based outcomes."""

from docxtpl import DocxTemplate  # type: ignore

from loguru import logger

from autodoc.outcome.outcome import Outcome
from autodoc.outcome.download_container import DownloadContainer
from autodoc.file_access import LinuxFileAccess


class WordOutcome(Outcome):
    """Word Outcome."""

    is_combination = False
    is_file = True

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
        temp_file = self.output_file_access.temp_file()
        self.document.save(temp_file)
        self.output_file_access.save_file()
        if self.download_container:
            self.download_container.add_file(file_path=self.output_file_access.path)
