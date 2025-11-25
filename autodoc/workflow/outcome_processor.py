"""Handle generating documents, represented by Outcomes."""

from pathlib import Path

from loguru import logger

from autodoc.data import DatabaseManager
from autodoc.data.tables import Outcome, OutcomeInstance, WorkflowInstance

from .outcome_service_factory import OutcomeServiceFactory


class OutcomeProcessor:
    """Processor of outcomes."""

    def __init__(self, outcome_service_factory: OutcomeServiceFactory, manager: DatabaseManager):
        """Create an OutcomeProcessor with a service factory and manager instance."""
        self.factory = outcome_service_factory
        self.manager = manager

    def process(
        self,
        outcomes: list[Outcome],
        contexts: list[dict],
        workflow_instance: WorkflowInstance,
        upload_mapping: dict,
        download_dir: Path,
    ):
        """
        Create all outcomes for each context.

        We create the outcome instances first before processing because it is
        being continuously queried by the user on the dashboard, so we want to
        load them all as "unfinished" so the user can see ok there are 100
        outcomes to be processed.

        Then we go through and actually process them.
        """
        outcome_array = self.build_outcome_instance_array(outcomes, contexts, workflow_instance)
        logger.info(f"Total outcome instances to process: {len(outcome_array)}")

        for outcome_info in outcome_array:
            outcome = outcome_info["outcome"]
            outcome_instance = outcome_info["instance"]
            context = outcome_info["context"]

            logger.debug(f"Processing {outcome_instance.Id=}, with context {context}")

            uploaded_filename = upload_mapping.get(outcome.Name)

            outcome_service = self.factory.create(
                outcome=outcome,
                download_dir=download_dir if outcome.is_download else None,
                template_uploaded_filename=uploaded_filename,
            )

            outcome_service.render(data=context)
            outcome_service.save()

            self.manager.outcome_instances.set_complete(outcome_instance_id=outcome_instance.Id)
            self.manager.outcome_instances.set_rendered_name(
                outcome_instance_id=outcome_instance.Id,
                rendered_name=outcome_service.output_storage_service.path.name,
            )

            self.manager.commit()

    def build_outcome_instance_array(
        self, outcomes: list[Outcome], contexts: list[dict], workflow_instance: WorkflowInstance
    ) -> list[dict]:
        """Return a full expanded list of each outcome and the context used to build it."""
        outcome_array = []
        """
        each outcome array is: {
            outcome: Outcome,
            outcome_instance: OutcomeInstance,
            context: context,
        }
        """
        for outcome in outcomes:
            for context in contexts:
                outcome_instance: OutcomeInstance = self.manager.outcome_instances.add(
                    outcome_id=outcome.Id, instance_id=workflow_instance.Id
                )
                self.manager.commit()

                outcome_array.append(
                    {
                        "outcome": outcome,
                        "instance": outcome_instance,
                        "context": context,
                    }
                )

        return outcome_array

    def downloads_exist(self, outcomes: list[Outcome]) -> bool:
        """Return whether downloads exist in the outcomes and therefore need to be zipped."""
        return any([outcome.DownloadName for outcome in outcomes])
