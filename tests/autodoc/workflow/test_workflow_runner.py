"""Test WorkflowRunner."""

from unittest.mock import call

from werkzeug.datastructures import FileStorage

from autodoc.workflow.workflow import WorkflowRunner


def test_workflow_runner_init_with_mocks(
    instance_id,
    mock_manager,
    mock_source_loader,
    mock_outcome_processor,
    mock_archiver,
    form_data,
    upload_mapping,
    test_download_dir,
):
    """Test that the WorkflowRunner initializes correctly using mocked dependencies."""
    runner = WorkflowRunner(
        instance_id=instance_id,
        manager=mock_manager,
        source_loader=mock_source_loader,
        outcome_processor=mock_outcome_processor,
        archiver=mock_archiver,
        form_data=form_data,
        upload_mapping=upload_mapping,
    )

    # Assert that the runner correctly fetched data via the mocked manager
    mock_manager.workflow_instances.get.assert_called_once_with(instance_id=instance_id)
    mock_manager.sources.get_all.assert_called_once_with(workflow_id=runner.workflow_id)
    mock_manager.outcomes.get_all.assert_called_once_with(workflow_id=runner.workflow_id)

    # Assert that the download directory was created inside our temp path
    assert (test_download_dir / str(instance_id)).is_dir()

    # Assert that form data is handled correctly

    form_data_choices = [{}, None, form_data, {"a": "b", "something": FileStorage()}]
    initial_data_expected = [{}, {}, form_data, {"a": "b"}]

    for _form_data, initial_data in zip(form_data_choices, initial_data_expected, strict=True):
        runner = WorkflowRunner(
            instance_id=instance_id,
            manager=mock_manager,
            source_loader=mock_source_loader,
            outcome_processor=mock_outcome_processor,
            archiver=mock_archiver,
            form_data=_form_data,
            upload_mapping=upload_mapping,
        )

        assert runner.initial_data == initial_data


def test_workflow_runner_process_success_path(
    mock_manager,
    mock_source_loader,
    mock_outcome_processor,
    mock_archiver,
    test_download_dir,
):
    """Test the successful process flow."""
    runner = WorkflowRunner(
        instance_id=1,
        manager=mock_manager,
        source_loader=mock_source_loader,
        outcome_processor=mock_outcome_processor,
        archiver=mock_archiver,
    )

    # Run the main process
    runner.process()

    # Assert that the orchestration logic is correct
    mock_source_loader.check.assert_called_once()
    mock_source_loader.build_contexts.assert_called_once()
    mock_outcome_processor.process.assert_called_once()
    mock_outcome_processor.downloads_exist.assert_called_once()
    mock_archiver.zip_downloads.assert_called_once()

    # Check that the final status is "Complete"
    mock_manager.workflow_instances.update_status.assert_called_with(
        instance_id=1, status="Complete"
    )


def test_workflow_runner_process_failure_path(
    mock_manager,
    mock_source_loader,
    mock_outcome_processor,
    mock_archiver,
    test_download_dir,
):
    """Test the successful process flow."""
    mock_source_loader.check.return_value = (False, ["Failure reason 1", "Failure reason 2"])

    runner = WorkflowRunner(
        instance_id=1,
        manager=mock_manager,
        source_loader=mock_source_loader,
        outcome_processor=mock_outcome_processor,
        archiver=mock_archiver,
    )

    # Run the main process
    runner.process()

    # Assert that the orchestration logic is correct
    mock_source_loader.check.assert_called_once()

    reasons_text = "Failure reason 1|Failure reason 2"
    mock_manager.workflow_instances.add_failure_reasons.assert_called_once_with(
        instance_id=1, reasons=reasons_text
    )

    mock_source_loader.build_contexts.assert_not_called()
    mock_outcome_processor.process.assert_not_called()
    mock_outcome_processor.downloads_exist.assert_not_called()

    # Check that the final status is "Failure"
    mock_manager.workflow_instances.update_status.assert_called_with(
        instance_id=1, status="Failure"
    )


def test_workflow_runner_with_no_downloads(
    mock_manager,
    mock_source_loader,
    mock_outcome_processor,
    mock_archiver,
    test_download_dir,
):
    """Test that files aren't zipped if no downloads_exist."""
    mock_outcome_processor.downloads_exist.return_value = False

    runner = WorkflowRunner(
        instance_id=1,
        manager=mock_manager,
        source_loader=mock_source_loader,
        outcome_processor=mock_outcome_processor,
        archiver=mock_archiver,
    )

    runner.process()

    mock_archiver.zip_downloads.assert_not_called()

    assert (
        call(instance_id=1, status="Zipping Outcomes for Download")
        not in mock_manager.workflow_instances.update_status.call_args_list
    )
    assert (
        call(instance_id=1, status="Complete")
        in mock_manager.workflow_instances.update_status.call_args_list
    )
