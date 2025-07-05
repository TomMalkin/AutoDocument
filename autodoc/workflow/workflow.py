"""Define the Workflow class that is a blueprint for workflow instances."""

from datetime import datetime
from typing import Optional

from loguru import logger

from autodoc.data.manager import DatabaseManager
from autodoc.outcome import outcome_service_map
from autodoc.outcome.download_container import DownloadContainer
from autodoc.source import source_service_map
from autodoc.workflow.event_logger import EventLoggerInterface


class Workflow:
    """A blueprint for the workflow instance."""

    start_time: datetime
    end_time: datetime

    def __init__(
        self,
        workflow_id: int,
        event_logger: EventLoggerInterface | None,
        manager: DatabaseManager,
        form_data: Optional[dict] = None,
        step: int = 1,
        parent_instance_id: Optional[int] = None,
    ) -> None:
        """Initialise a workflow with a workflow_id."""
        self.manager = manager
        self.workflow_id = workflow_id
        self.data = form_data or {}
        # self.name = manager.get_workflow_name(workflow_id=workflow_id)
        self.name = self.manager.workflows.get(workflow_id=workflow_id).Name
        self.step = step
        self.parent_instance_id = parent_instance_id
        self.event_logger = event_logger
        self.instance_id: int

    def process(self, download_container: DownloadContainer, upload_mapping=None) -> None:
        """
        Process the sources, and if the sources haven't been split, outcomes.

        upload mapping is the field name -> filename
        for example "Client Record": "dashboard/files/client_record.csv"
        """
        if not upload_mapping:
            upload_mapping = {}

        self.start_time = datetime.now()

        if self.parent_instance_id:
            instance = self.manager.workflow_instances.add_split(
                parent_instance_id=self.parent_instance_id,
                start_time=self.start_time,
                step=self.step,
            )
            self.instance_id = instance.InstanceId

        else:
            instance = self.manager.workflow_instances.add(
                workflow_id=self.workflow_id, step=self.step
            )
            self.instance_id = instance.InstanceId

        result = self.process_sources(
            download_container=download_container, upload_mapping=upload_mapping
        )

        logger.info(f"result of sources process is {result}")
        logger.info(f"final data after all sources is {self.data}")

        if result:
            self.process_outcomes(
                download_container=download_container,
                upload_mapping=upload_mapping,
            )

        self.end_time = datetime.now()

    def process_sources(self, download_container: DownloadContainer, upload_mapping: dict) -> bool:
        """
        Process the sources.

        Process in step order for this workflow, returning whether outcomes should be processed.
        """
        self.sources = self.manager.sources.get_all_from_step(
            workflow_id=self.workflow_id, step=self.step
        )

        logger.info(f"{len(self.sources)} sources identified for >= step {self.step}")

        for source in self.sources:
            logger.info(f"processing source_id {source.Id}")

            uploaded_filename = upload_mapping.get(source.Name)

            source_type = source.source_type.Name
            source_service_class = source_service_map[source_type]
            source_service = source_service_class(source=source, uploaded_filename=uploaded_filename)
            source_service.load_data(current_data=self.data)

            if source_service.is_multi_record:
                if source.Splitter:
                    for record in source_service.data:
                        split_workflow = Workflow(
                            workflow_id=self.workflow_id,
                            event_logger=self.event_logger,
                            form_data=self.data | record,
                            step=source.Step + 1,
                            parent_instance_id=self.instance_id,
                            manager=self.manager,
                        )
                        split_workflow.process(
                            download_container=download_container, upload_mapping=upload_mapping
                        )
                    return False
                else:
                    new_data = {source.FieldName: source_service.data}
                    self.write_data(data=new_data)

            else:
                self.write_data(data=source_service.data)

        return True

    def write_data(self, data: dict) -> None:
        """Once new data has been obtained from a source, write it to self.data."""
        for key, value in data.items():
            if key in self.data.keys():
                logger.warning(f"WARNING: Key {key} being overwritten")
            self.data[key] = value

    def process_outcomes(self, download_container: DownloadContainer, upload_mapping: dict) -> None:
        """Write all the outcomes for the workflow."""
        self.outcomes = self.manager.outcomes.get_all(workflow_id=self.workflow_id)

        logger.info(f"{len(self.outcomes)} outcomes identified.")

        for outcome in self.outcomes:
            logger.info(f"processing outcome_id {outcome.Id}")

            if upload_mapping.get(outcome.Name):
                uploaded_filename = upload_mapping[outcome.Name]

            else:
                uploaded_filename = None

            outcome_type = outcome.outcome_type.Name
            outcome_service_class = outcome_service_map[outcome_type]
            outcome_service = outcome_service_class(
                outcome,
                download_container=download_container if outcome.is_download else None,
                template_uploaded_filename=uploaded_filename,
            )

            outcome_service.render(data=self.data)
            outcome_service.save()
