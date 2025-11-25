"""pytest fixtures."""

from unittest.mock import MagicMock

import pytest

from autodoc.data.manager import DatabaseManager
from autodoc.data.tables import Outcome, Source, Workflow, WorkflowInstance
from autodoc.workflow.archiver import Archiver
from autodoc.workflow.outcome_processor import OutcomeProcessor
from autodoc.workflow.outcome_service_factory import OutcomeServiceFactory
from autodoc.workflow.source_loader import SourceLoader
from autodoc.workflow.source_service_factory import SourceServiceFactory

# =================================================
# 1. Core Test Data Fixtures
# These provide simple, reusable data for your tests.
# =================================================


@pytest.fixture
def instance_id():
    """Provide a consistent instance ID for tests."""
    return 1


@pytest.fixture
def workflow_id():
    """Provide a consistent workflow ID for tests."""
    return 101


@pytest.fixture
def form_data():
    """Provide sample form data passed from the UI."""
    return {"client_name": "Test Client", "invoice_number": 23}


@pytest.fixture
def upload_mapping():
    """Provide a sample mapping of upload names to file paths."""
    return {"Client Data CSV": "/tmp/uploads/client_data.csv"}


# =================================================
# 2. Dependency Mocking Fixtures (for Unit Testing)
# These mock the behavior of WorkflowRunner's dependencies.
# =================================================


@pytest.fixture
def mock_source_loader():
    """Fixture for a mocked SourceLoader."""
    loader = MagicMock(spec=SourceLoader)
    # Default successful check
    loader.check.return_value = (True, [])
    # Default context build
    loader.build_contexts.return_value = [{"client_name": "Test Client"}]
    return loader


@pytest.fixture
def mock_outcome_processor():
    """Fixture for a mocked OutcomeProcessor."""
    processor = MagicMock(spec=OutcomeProcessor)
    processor.downloads_exist.return_value = True
    return processor


@pytest.fixture
def mock_archiver():
    """Fixture for a mocked Archiver."""
    return MagicMock(spec=Archiver)


@pytest.fixture
def mock_source_service_factory():
    """Fixture for a mocked SourceServiceFactory."""
    factory = MagicMock(spec=SourceServiceFactory)
    return factory


@pytest.fixture
def mock_outcome_service_factory():
    """Fixture for a mocked SourceServiceFactory."""
    factory = MagicMock(spec=OutcomeServiceFactory)
    return factory


# =================================================
# 3. Database Fixtures
# A fully mocked manager for pure unit tests.
# =================================================


@pytest.fixture
def mock_manager(instance_id, workflow_id):
    """
    Provide a fully mocked DatabaseManager.

    Useful for unit testing WorkflowRunner's logic without touching a real database.
    """
    manager = MagicMock(spec=DatabaseManager)

    # Mock the data returned from the database
    mock_workflow = MagicMock(spec=Workflow)
    mock_workflow.has_download = True

    mock_instance = MagicMock(spec=WorkflowInstance)
    mock_instance.Id = instance_id
    mock_instance.WorkflowId = workflow_id
    mock_instance.workflow = mock_workflow

    mock_source = MagicMock(spec=Source)
    mock_outcome = MagicMock(spec=Outcome)

    # Configure the manager's repositories to return these mocks
    manager.workflow_instances.get.return_value = mock_instance
    manager.sources.get_all.return_value = [mock_source]
    manager.outcomes.get_all.return_value = [mock_outcome]

    return manager


# =================================================
# 4. Environment & Configuration Fixtures
# =================================================


@pytest.fixture
def test_download_dir(tmp_path, monkeypatch):
    """
    Create a temporary download directory for a test run and patches the config.

    This prevents tests from creating directories in your actual project.
    """
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()

    # Use monkeypatch to temporarily change the DOWNLOAD_DIRECTORY config value
    monkeypatch.setattr("autodoc.workflow.workflow.DOWNLOAD_DIRECTORY", download_dir)

    return download_dir


# =================================================
# 5. Mock Tables
# =================================================
