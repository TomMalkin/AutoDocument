"""Handle source list based processes, like checking and building contexts."""

from loguru import logger

from autodoc.data import DatabaseManager
from autodoc.data.tables import Source, WorkflowInstance
from autodoc.source import SourceService

from .source_service_factory import SourceServiceFactory


class SourceLoader:
    """Service class for SourceService based processes."""

    def __init__(self, source_service_factory: SourceServiceFactory, manager: DatabaseManager):
        """Create this service."""
        self.factory = source_service_factory
        self.manager = manager

    def check(self, sources: list[Source], upload_mapping: dict) -> tuple[bool, list[str]]:
        """
        Run a check across all provided sources for common issues.

        If issues are found, then return False with a list of reasons.
        """
        checks = []
        for source in sources:
            uploaded_filename = upload_mapping.get(source.Name)
            source_service = self.factory.create(source, uploaded_filename)
            logger.info(f"Checking source id {source.Id}")
            checks.append(source_service.check())

        is_ok = all(x[0] for x in checks)
        reasons = [x[1] for x in checks if x[1]] if not is_ok else []
        logger.info(f"Checking all of {checks}, with a result of {is_ok}")
        return is_ok, reasons

    def build_contexts(
        self,
        sources: list[Source],
        workflow_instance: WorkflowInstance,
        initial_data: dict,
        upload_mapping: dict,
    ) -> list[dict]:
        """
        Build the contexts using cartesian expansion.

        initial_data: Is assumed to be cleaned of unusable data, such as FileStorage
        parts of a Form.
        """
        contexts = [initial_data]
        logger.info(f"Building contexts for {workflow_instance.Id=} with {initial_data=}")

        for source in sources:
            logger.info(f"processing {source.Id=}: {source.source_type.Name}")

            uploaded_filename = upload_mapping.get(source.Name)
            source_service: SourceService = self.factory.create(
                source=source, uploaded_filename=uploaded_filename
            )
            assert isinstance(source_service, SourceService)

            source_instance = self.manager.source_instances.add(
                source_id=source.Id, instance_id=workflow_instance.Id
            )
            self.manager.commit()

            next_contexts = []

            for context in contexts:
                source_service.load_data(current_data=context)

                if source_service.is_multi_record:
                    if source_service.source.Splitter:
                        for record in source_service.data:
                            merged = context.copy()
                            merged.update(record)
                            next_contexts.append(merged)

                    else:
                        merged = context.copy()
                        merged.update({source_service.source.FieldName: source_service.data})
                        next_contexts.append(merged)

                else:
                    merged = context.copy()
                    merged.update(source_service.data)
                    next_contexts.append(merged)

            contexts = next_contexts

            self.manager.source_instances.set_loaded(source_instance_id=source_instance.Id)
            self.manager.commit()

        return contexts
