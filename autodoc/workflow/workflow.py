"""Define the Workflow class that is a blueprint for workflow instances."""

from typing import Optional

from loguru import logger

from autodoc.outcome import Outcome, outcome_map

# from autodoc.outcome import download_container
from autodoc.outcome.download_container import DownloadContainer
from autodoc.source import source_map
from autodoc.db import DatabaseManager
from autodoc.containers import RecordSet
from autodoc.workflow.event_logger import EventLoggerInterface
from datetime import datetime
from json import dumps


class Workflow:
    """A blueprint for the workflow instance."""

    start_time: datetime
    end_time: datetime

    @staticmethod
    def get_form(workflow_id: int, manager: DatabaseManager) -> RecordSet:
        """Get the initial form details for a given workflow."""
        return manager.get_form(workflow_id)

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
        self.workflow_id = workflow_id
        self.data = form_data or {}
        self.name = manager.get_workflow_name(workflow_id=workflow_id)
        self.step = step
        self.parent_instance_id = parent_instance_id
        self.event_logger = event_logger
        self.instance_id: int

        self.manager = manager

    def write_instance(self):
        """Write the instance to the database."""
        logger.warning("Writing instance")
        sql = """
            insert into WorkflowInstance
            (ParentInstanceId, WorkflowId, StartTime, EndTime, Completed, Data, Step)
            values
            (:parent_instance_id, :workflow_id, :start_time, :end_time, :completed, :data, :step)
        """
        params = {
            "parent_instance_id": self.parent_instance_id,
            "workflow_id": self.workflow_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "completed": 1,
            "data": dumps(self.data),
            "step": None,
        }
        # self.manager.db.execute(sql, params)

    def process(self, download_container: DownloadContainer, upload_mapping=None) -> None:
        """
        Process the sources, and if the sources haven't been split, outcomes.

        upload mapping is the field name -> filename
        for example "Client Record": "dashboard/files/client_record.csv"
        """
        self.start_time = datetime.now()

        if self.parent_instance_id:
            self.instance_id = self.manager.create_split_workflow_instance(
                workflow_id=self.workflow_id,
                parent_instance_id=self.parent_instance_id,
                step=self.step,
            )

        else:
            self.instance_id = self.manager.create_workflow_instance(
                workflow_id=self.workflow_id, step=self.step
            )

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

    def process_sources(
        self, download_container: DownloadContainer, upload_mapping: dict | None = None
    ) -> bool:
        """
        Process the sources.

        Process in step order for this workflow, returning whether outcomes should be processed.
        """
        self.sources_details = self.manager.get_sources(
            workflow_id=self.workflow_id,
            step=self.step,
        ).data

        logger.info(f"{len(self.sources_details)} sources identified")

        for source_details in self.sources_details:
            logger.info(f"processing source_id {source_details['SourceId']}")

            if upload_mapping and upload_mapping.get(source_details["SourceName"]):
                # this is a file upload source
                uploaded_filename = upload_mapping[source_details["SourceName"]]

            else:
                uploaded_filename = None

            source = source_map[source_details["TypeName"]](
                source_details=source_details,
                manager=self.manager,
                uploaded_filename=uploaded_filename,
            )
            source.load_data(current_data=self.data)

            if source.is_multi_record:
                if source_details["Splitter"]:
                    for record in source.data:
                        split_workflow = Workflow(
                            workflow_id=self.workflow_id,
                            event_logger=self.event_logger,
                            form_data=self.data | record,
                            step=source_details["Step"] + 1,
                            parent_instance_id=self.instance_id,
                            manager=self.manager,
                        )
                        split_workflow.process(
                            download_container=download_container, upload_mapping=upload_mapping
                        )
                    return False
                else:
                    new_data = {source_details["FieldName"]: source.data}
                    self.write_data(data=new_data, source_id=source_details["SourceId"])

            else:
                self.write_data(data=source.data, source_id=source_details["SourceId"])

        return True

    def write_data(self, data: dict, source_id: int) -> None:
        """Once new data has been obtained from a source, write it to self.data."""
        for key, value in data.items():
            if key in self.data.keys():
                logger.warning(f"WARNING: Key {key} being overwritten")
            self.data[key] = value

    def process_outcomes(
        self,
        download_container: DownloadContainer,
        upload_mapping=None,
    ) -> None:
        """Write all the outcomes for the workflow."""
        self.outcomes_details = self.manager.get_outcomes(workflow_id=self.workflow_id).data

        outcome: Outcome

        logger.info(f"{len(self.outcomes_details)} outcomes identified.")

        for outcome_details in self.outcomes_details:
            logger.info(f"processing outcome_id {outcome_details['OutcomeId']}")

            if upload_mapping and upload_mapping.get(outcome_details["OutcomeName"]):
                # this is a file upload outcome
                uploaded_filename = upload_mapping[outcome_details["OutcomeName"]]

            else:
                uploaded_filename = None

            if outcome_details["FilterField"]:
                if self.data.get(outcome_details["FilterField"]) != outcome_details["FilterValue"]:
                    continue

            if outcome_details["OutputFileTypeName"] == "Download":
                outcome = outcome_map[outcome_details["OutcomeTypeName"]](
                    outcome_details,
                    download_container=download_container,
                    template_uploaded_filename=uploaded_filename,
                )
            else:
                outcome = outcome_map[outcome_details["OutcomeTypeName"]](
                    outcome_details,
                    download_container=None,
                    template_uploaded_filename=uploaded_filename,
                )

            outcome.render(data=self.data)
            outcome.save()
