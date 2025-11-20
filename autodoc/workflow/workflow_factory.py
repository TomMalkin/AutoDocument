"""Define the Workflow Runner Factory."""

from typing import Optional

from autodoc.data import DatabaseManager

from .archiver import Archiver
from .outcome_processor import OutcomeProcessor
from .outcome_service_factory import OutcomeServiceFactory
from .source_loader import SourceLoader
from .source_service_factory import SourceServiceFactory
from .workflow import WorkflowRunner


class WorkflowRunnerFactory:
    """Factory that creates a WorfklowRunner."""

    @staticmethod
    def create_runner(
        instance_id: int,
        manager: DatabaseManager,
        form_data: Optional[dict] = None,
        upload_mapping: Optional[dict] = None,
    ):
        """Create a Workflow Runner from an instance Id."""
        source_service_factory = SourceServiceFactory()
        outcome_service_factory = OutcomeServiceFactory()

        source_loader = SourceLoader(
            source_service_factory=source_service_factory,
            manager=manager,
        )
        outcome_processor = OutcomeProcessor(
            outcome_service_factory=outcome_service_factory, manager=manager
        )
        archiver = Archiver()

        return WorkflowRunner(
            instance_id=instance_id,
            manager=manager,
            source_loader=source_loader,
            outcome_processor=outcome_processor,
            archiver=archiver,
            form_data=form_data,
            upload_mapping=upload_mapping,
        )
