"""Define the DatabaseManager class that manages a Session and exposes repositories."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .base import Base
from .repositories import (
    DatabaseMetaSourceRepository,
    FileTemplateRepository,
    FormFieldRepository,
    OutcomeRepository,
    OutcomeTypeRepository,
    SourceRepository,
    SourceTypeRepository,
    SQLFieldsRepository,
    StorageInstanceRepository,
    StorageTypeRepository,
    WorkflowInstanceRepository,
    WorkflowRepository,
    LLMProviderRepository,
    LLMRepository,
)


class DatabaseManager:
    """Manage a single SQLAlchemy session and expose Repository objects."""

    def __init__(self, db_file: str):
        """Create a Database Manager with a given db_file."""
        self.engine = create_engine(f"sqlite:///{db_file}")
        Base.metadata.create_all(self.engine)
        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._session: Session | None = None

    def _get_current_session(self) -> Session:
        """Lazily create and return a SQLAlchemy session for the current request."""
        if self._session is None:
            self._session = self._SessionLocal()
        return self._session

    @property
    def workflows(self) -> WorkflowRepository:
        """Provide access to the WorkflowRepository for the current session."""
        return WorkflowRepository(self._get_current_session())

    @property
    def sources(self) -> SourceRepository:
        """Provide access to the ProductRepository for the current session."""
        return SourceRepository(self._get_current_session())

    @property
    def sql_fields(self) -> SQLFieldsRepository:
        """Provide access to the SQLFieldsRepository for the current session."""
        return SQLFieldsRepository(self._get_current_session())

    @property
    def form_fields(self) -> FormFieldRepository:
        """Provide access to the FormFieldRepository for the current session."""
        return FormFieldRepository(self._get_current_session())

    @property
    def workflow_instances(self) -> WorkflowInstanceRepository:
        """Provide access to the WorkflowInstanceRepository for the current session."""
        return WorkflowInstanceRepository(self._get_current_session())

    @property
    def database_meta_sources(self) -> DatabaseMetaSourceRepository:
        """Provide access to the DatabaseMetaSourceRepository for the current session."""
        return DatabaseMetaSourceRepository(self._get_current_session())

    @property
    def outcome_types(self) -> OutcomeTypeRepository:
        """Provide access to the OutcomeTypeRepository for the current session."""
        return OutcomeTypeRepository(self._get_current_session())

    @property
    def source_types(self) -> SourceTypeRepository:
        """Provide access to the SourceTypeRepository for the current session."""
        return SourceTypeRepository(self._get_current_session())

    @property
    def storage_types(self) -> StorageTypeRepository:
        """Provide access to the Storage Types for the current session."""
        return StorageTypeRepository(self._get_current_session())

    @property
    def storage_instances(self) -> StorageInstanceRepository:
        """Provide access to Storage Instances for the current session."""
        return StorageInstanceRepository(self._get_current_session())

    @property
    def file_templates(self) -> FileTemplateRepository:
        """Provide access to File Templates  for the current session."""
        return FileTemplateRepository(self._get_current_session())

    @property
    def outcomes(self) -> OutcomeRepository:
        """Provide access to the OutcomeRepository for the current session."""
        return OutcomeRepository(self._get_current_session())

    @property
    def llms(self) -> LLMRepository:
        """Provide access to the LLMRepository for the current session."""
        return LLMRepository(self._get_current_session())

    @property
    def llm_providers(self) -> LLMProviderRepository:
        """Provide access to the LLMProviderRepository for the current session."""
        return LLMProviderRepository(self._get_current_session())


    # @property
    # def v_file_accessors(self) -> VFileAccessorsRepository:
    #     """Provide access to the VFileAccessorsRepository for the current session."""
    #     return VFileAccessorsRepository(self._get_current_session())
    #
    # @property
    # def v_outcomes(self) -> VOutcomeRepository:
    #     """Provide access to the VOutcomes for the current session."""
    #     return VOutcomeRepository(self._get_current_session())

    # @property
    # def storage_service(self) -> StorageService:
    #     """Return a Storage Service."""
    #     return StorageService(instance_repo=self.storage_instances, type_repo=self.storage_types)

    def commit(self):
        """Commit the current session's transaction."""
        if self._session:
            self._session.commit()

    def rollback(self):
        """Roll back the current session's transaction."""
        if self._session:
            self._session.rollback()

    def close(self):
        """Close the current session."""
        if self._session:
            self._session.close()
            self._session = None
