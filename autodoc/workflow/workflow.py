"""Define the Workflow class that is a blueprint for workflow instances."""

import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from werkzeug.datastructures import FileStorage

from autodoc.config import DOWNLOAD_DIRECTORY
from autodoc.data.manager import DatabaseManager
from autodoc.data.tables import WorkflowInstance
from autodoc.outcome import outcome_service_map
from autodoc.source import source_service_map


class Workflow:
    """A blueprint for the workflow instance."""

    start_time: datetime
    end_time: datetime

    def __init__(
        self,
        workflow_id: int,
        manager: DatabaseManager,
        form_data: Optional[dict] = None,
        upload_mapping: Optional[dict] = None,
    ) -> None:
        """Initialise a workflow with a workflow_id."""
        self.manager: DatabaseManager = manager
        self.workflow_id = workflow_id
        self.data = form_data or {}
        self.name = self.manager.workflows.get(workflow_id=workflow_id).Name
        self.instance: WorkflowInstance
        self.upload_mapping = upload_mapping or {}

        self.sources = self.manager.sources.get_all_from_step(workflow_id=self.workflow_id, step=1)
        self.workflow = self.manager.workflows.get(workflow_id=workflow_id)

        self.download_dir_base: Path = DOWNLOAD_DIRECTORY
        self.download_dir: Path

    @classmethod
    def from_instance_id(
        cls,
        instance_id: int,
        manager: DatabaseManager,
        upload_mapping: Optional[dict],
        form_data: Optional[dict],
    ):
        """
        Load a workflow from a preexisting instance.

        Useful for setting an instance and then having another process complete it.
        """
        instance = manager.workflow_instances.get(instance_id=instance_id)
        workflow_id = instance.WorkflowId
        workflow = cls(
            workflow_id=workflow_id,
            manager=manager,
            form_data=form_data,
            upload_mapping=upload_mapping,
        )
        workflow.set_instance(instance_id=instance_id)

        return workflow

    def create_instance(self):
        """Create an instance object for this workflow."""
        self.instance = self.manager.workflow_instances.add(workflow_id=self.workflow_id)
        self.manager.commit()

    def set_instance(self, instance_id: int):
        """Set an existing instance."""
        self.instance = self.manager.workflow_instances.get(instance_id=instance_id)

    def process(self):
        """Create an instance of this workflow and produce outcomes."""
        # self.set_instance()

        logger.info(f"Processing with {self.workflow_id=}, {self.instance.Id=}")

        self.download_dir = self.download_dir_base / str(self.instance.Id)

        self.download_dir.mkdir(exist_ok=True)

        logger.info(f"Processing Workflow Instance {self.instance.Id}")

        self.contexts = self.build_contexts()

        self.process_outcomes()

        self.manager.workflow_instances.update_status(
            instance_id=self.instance.Id,
            status="Zipping",
        )
        self.manager.commit()

        self.zip_downloads()

        self.manager.workflow_instances.update_status(
            instance_id=self.instance.Id,
            status="Complete",
        )
        self.manager.commit()

    def zip_downloads(self):
        """If a process is finished, then zip any downloads."""
        if any([outcome.DownloadName for outcome in self.workflow.outcomes]):
            logger.info("Downloads found so zipping.")
            files_to_zip = [f for f in self.download_dir.iterdir() if f.is_file()]

            if files_to_zip:
                zip_filename = self.download_dir.name + ".zip"
                zip_filepath = self.download_dir.parent / zip_filename

                with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files_to_zip:
                        zipf.write(file_path, arcname=file_path.name)
        else:
            logger.info("No downloads found, so not zipping")


    @property
    def zip_filepath(self) -> Path:
        """The location of this instances download zip file."""
        zip_filename = self.download_dir.name + ".zip"
        return self.download_dir.parent / zip_filename


    def build_contexts(self) -> list[dict[str, Any]]:
        """Build the contexts using cartesian expansion."""
        logger.info("Building Contexts")

        usable_data = {k: v for k, v in self.data.items() if not isinstance(v, FileStorage)}
        contexts = [usable_data]

        logger.info(f"Starting context (from forms etc) {contexts}")

        for source in self.sources:
            source_type = source.source_type.Name
            logger.info(f"processing source_id {source.Id}: {source_type}")

            uploaded_filename = self.upload_mapping.get(source.Name)
            logger.info(f"{uploaded_filename=}")

            source_service_class = source_service_map[source_type]
            source_service = source_service_class(
                source=source, uploaded_filename=uploaded_filename
            )

            # create source instance
            source_instance = self.manager.source_instances.add(
                source_id=source.Id, instance_id=self.instance.Id
            )
            self.manager.commit()

            source_service.load_data(current_data=self.data)

            self.manager.source_instances.set_loaded(source_instance_id=source_instance.Id)
            self.manager.commit()

            logger.info(f"contexts before loading: {contexts}")

            contexts = self.expand(contexts, source_service)

            logger.info(f"contexts after loading: {contexts}")

        return contexts

    def expand(self, contexts, source_service) -> list[dict[str, Any]]:
        """Expand with new contexts."""
        new_contexts = []
        for context in contexts:
            if source_service.is_multi_record:
                if source_service.source.Splitter:
                    for record in source_service.data:
                        merged = context.copy()
                        merged.update(record)
                        new_contexts.append(merged)
                else:
                    merged = context.copy()
                    merged.update({source_service.source.FieldName: source_service.data})
                    new_contexts.append(merged)

            else:
                merged = context.copy()
                merged.update(source_service.data)
                new_contexts.append(merged)

        return new_contexts

    def process_outcomes(self) -> None:
        """Write all the outcomes for the workflow."""
        self.outcomes = self.manager.outcomes.get_all(workflow_id=self.workflow_id)

        logger.info(f"{len(self.outcomes)} different outcomes identified.")

        outcome_array = []
        """
        each outcome array is: {
            outcome: Outcome,
            outcome_instance: OutcomeInstance,
            context: context,
        }
        """

        for outcome in self.outcomes:
            for context in self.contexts:
                outcome_instance = self.manager.outcome_instances.add(
                    outcome_id=outcome.Id, instance_id=self.instance.Id
                )
                self.manager.commit()

                outcome_array.append(
                    {
                        "outcome": outcome,
                        "instance": outcome_instance,
                        "context": context,
                    }
                )

        logger.info(f"Total outcomes: {len(outcome_array)}")

        for outcome_info in outcome_array:
            outcome = outcome_info["outcome"]
            outcome_instance = outcome_info["instance"]
            context = outcome_info["context"]

            logger.info(
                f"Processing Outcome Instance {outcome_instance.Id}, with context {context}"
            )

            if self.upload_mapping.get(outcome.Name):
                uploaded_filename = self.upload_mapping[outcome.Name]
                logger.info(f"The uploaded filename for this outcome is {uploaded_filename}")

            else:
                uploaded_filename = None
                logger.info("This outcome wasn't uploaded")

            outcome_type = outcome.outcome_type.Name
            outcome_service_class = outcome_service_map[outcome_type]
            outcome_service = outcome_service_class(
                outcome=outcome,
                download_dir=self.download_dir if outcome.is_download else None,
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
