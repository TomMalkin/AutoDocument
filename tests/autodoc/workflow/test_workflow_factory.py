"""Test the WorkflowRunnerFactory."""

from autodoc.workflow.archiver import Archiver
from autodoc.workflow.outcome_processor import OutcomeProcessor
from autodoc.workflow.outcome_service_factory import OutcomeServiceFactory
from autodoc.workflow.source_loader import SourceLoader
from autodoc.workflow.source_service_factory import SourceServiceFactory
from autodoc.workflow.workflow import WorkflowRunner
from autodoc.workflow.workflow_factory import WorkflowRunnerFactory


def test_create_runner_builds_correctly(instance_id, mock_manager, form_data, upload_mapping):
    """Test that create_runner builds correctly."""
    runner = WorkflowRunnerFactory.create_runner(
        instance_id=instance_id,
        manager=mock_manager,
        form_data=form_data,
        upload_mapping=upload_mapping,
    )

    # 2. ASSERT: Check the created object and its dependencies

    # --- Top-level verification ---
    assert isinstance(runner, WorkflowRunner), "Factory should return a WorkflowRunner instance"
    assert runner.manager is mock_manager, "The manager should be passed through correctly"

    # The factory calls manager.workflow_instances.get() to create the instance object
    mock_manager.workflow_instances.get.assert_called_once_with(instance_id=instance_id)

    # --- Verify data was passed through correctly ---
    assert runner.initial_data == form_data
    assert runner.upload_mapping == upload_mapping

    # --- Verify dependency types ---
    assert isinstance(runner.source_loader, SourceLoader), (
        "SourceLoader dependency was not created correctly"
    )
    assert isinstance(runner.outcome_processor, OutcomeProcessor), (
        "OutcomeProcessor dependency was not created correctly"
    )
    assert isinstance(runner.archiver, Archiver), "Archiver dependency was not created correctly"

    # --- Verify "grandchild" dependencies (dependencies of the dependencies) ---
    # Check that the manager was correctly passed down to the next level
    assert runner.source_loader.manager is mock_manager, "Manager was not passed to SourceLoader"
    assert runner.outcome_processor.manager is mock_manager, (
        "Manager was not passed to OutcomeProcessor"
    )

    # Check that the sub-factories were created and passed down
    assert isinstance(runner.source_loader.factory, SourceServiceFactory), (
        "SourceServiceFactory was not passed to SourceLoader"
    )
    assert isinstance(runner.outcome_processor.factory, OutcomeServiceFactory), (
        "OutcomeServiceFactory was not passed to OutcomeProcessor"
    )
