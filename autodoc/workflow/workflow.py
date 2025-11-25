"""Define the Workflow class that is a blueprint for workflow instances."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from werkzeug.datastructures import FileStorage

from autodoc.config import DOWNLOAD_DIRECTORY
from autodoc.data.manager import DatabaseManager
from autodoc.data.tables import Outcome, Source, Workflow, WorkflowInstance

from .archiver import Archiver
from .outcome_processor import OutcomeProcessor
from .source_loader import SourceLoader


class WorkflowRunner:
    """An orchestrator of a Workflow Instance."""

    start_time: datetime
    end_time: datetime

    def __init__(
        self,
        instance_id: int,
        manager: DatabaseManager,
        source_loader: SourceLoader,
        outcome_processor: OutcomeProcessor,
        archiver: Archiver,
        form_data: Optional[dict] = None,
        upload_mapping: Optional[dict] = None,
    ) -> None:
        """Create a Runner with an instance id."""
        self.manager: DatabaseManager = manager
        self.instance: WorkflowInstance = manager.workflow_instances.get(instance_id=instance_id)
        self.workflow: Workflow = self.instance.workflow

        self.workflow_id = self.instance.WorkflowId

        if form_data:
            self.initial_data = {
                k: v for k, v in form_data.items() if not isinstance(v, FileStorage)
            }
        else:
            self.initial_data = {}
        self.upload_mapping = upload_mapping or {}

        self.source_loader = source_loader
        self.outcome_processor = outcome_processor
        self.archiver = archiver

        self.sources: list[Source] = self.manager.sources.get_all(workflow_id=self.workflow_id)
        self.outcomes: list[Outcome] = self.manager.outcomes.get_all(workflow_id=self.workflow_id)

        self.download_dir_base: Path = DOWNLOAD_DIRECTORY
        self.download_dir = self.download_dir_base / str(self.instance.Id)
        self.download_dir.mkdir(exist_ok=True)

    def process_failure(self, reasons: list[str]):
        """Handle if there is at least one problem in the Sources."""
        reasons_text = "|".join(r for r in reasons if r)

        self.manager.workflow_instances.add_failure_reasons(
            instance_id=self.instance.Id,
            reasons=reasons_text,
        )
        self.manager.commit()

        self.manager.workflow_instances.update_status(
            instance_id=self.instance.Id,
            status="Failure",
        )
        self.manager.commit()

    def set_instance_status(self, status: str):
        """Set the status of the instance."""
        self.manager.workflow_instances.update_status(
            instance_id=self.instance.Id,
            status=status,
        )
        self.manager.commit()

    def process(self):
        """Run this Instance."""
        logger.info(f"Processing with {self.workflow_id=}, {self.instance.Id=}")

        # run a preliminary check on common Source Loading issues.
        self.set_instance_status("Starting")
        check, reasons = self.source_loader.check(
            sources=self.sources, upload_mapping=self.upload_mapping
        )

        if not check:
            self.process_failure(reasons=reasons)
            return

        # Build the context
        self.set_instance_status("Building Context from Sources")
        contexts = self.source_loader.build_contexts(
            sources=self.sources,
            workflow_instance=self.instance,
            initial_data=self.initial_data,
            upload_mapping=self.upload_mapping,
        )

        self.set_instance_status("Creating Outcomes")
        self.outcome_processor.process(
            outcomes=self.outcomes,
            contexts=contexts,
            workflow_instance=self.instance,
            upload_mapping=self.upload_mapping,
            download_dir=self.download_dir,
        )

        if self.outcome_processor.downloads_exist(outcomes=self.outcomes):
            self.set_instance_status("Zipping Outcomes for Download")
            self.archiver.zip_downloads(download_dir=self.download_dir)

        self.set_instance_status("Complete")
