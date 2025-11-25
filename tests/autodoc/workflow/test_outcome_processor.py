"""Test the OutcomeProcessor."""

from pathlib import Path
from unittest.mock import MagicMock, call, patch

from autodoc.data.tables import Outcome, OutcomeInstance, WorkflowInstance
from autodoc.outcome import OutcomeService
from autodoc.workflow.outcome_processor import OutcomeProcessor


def test_builds_correctly(mock_outcome_service_factory, mock_manager):
    """Test if the OutcomeProcessor inits correctly."""
    outcome_processor = OutcomeProcessor(
        outcome_service_factory=mock_outcome_service_factory, manager=mock_manager
    )

    assert outcome_processor.factory is mock_outcome_service_factory
    assert outcome_processor.manager is mock_manager


def test_build_outcome_instance_array(mock_outcome_service_factory, mock_manager):
    """Test that build_outcome_array builds the correct list of outcomes."""
    # 1. ARRANGE
    mock_outcome_1 = MagicMock(spec=Outcome, Id=10)
    mock_outcome_2 = MagicMock(spec=Outcome, Id=20)
    outcomes = [mock_outcome_1, mock_outcome_2]

    # Create some sample contexts
    contexts = [{"client": "A"}, {"client": "B"}, {"client": "C"}]

    # Mock the workflow instance
    mock_workflow_instance = MagicMock(spec=WorkflowInstance, Id=1)

    # Mock the return value for the database 'add' call
    # Each time `add` is called, it should return a new mock instance
    mock_manager.outcome_instances.add.side_effect = [
        MagicMock(spec=OutcomeInstance, Id=i) for i in range(101, 107)
    ]

    processor = OutcomeProcessor(
        outcome_service_factory=mock_outcome_service_factory, manager=mock_manager
    )

    # 2. ACT
    outcome_array = processor.build_outcome_instance_array(
        outcomes=outcomes, contexts=contexts, workflow_instance=mock_workflow_instance
    )

    # 3. ASSERT
    # Check that we got 2 outcomes * 3 contexts = 6 total items
    assert len(outcome_array) == 6

    # Check that the database 'add' method was called 6 times
    assert mock_manager.outcome_instances.add.call_count == 6
    # Check that 'commit' was called after each 'add'
    assert mock_manager.commit.call_count == 6

    # Verify the arguments for the first and last calls to 'add'
    mock_manager.outcome_instances.add.assert_has_calls(
        [
            call(outcome_id=10, instance_id=1),
            call(outcome_id=20, instance_id=1),
        ]
    )

    # Check the structure of the first returned item
    assert outcome_array[0]["outcome"] is mock_outcome_1
    assert outcome_array[0]["context"] == {"client": "A"}
    assert outcome_array[0]["instance"].Id == 101  # From our side_effect


def test_process_method(mock_outcome_service_factory, mock_manager):
    """Test the main process method's orchestration logic."""
    # 1. ARRANGE
    processor = OutcomeProcessor(
        outcome_service_factory=mock_outcome_service_factory, manager=mock_manager
    )

    # Create mock data that `build_outcome_instance_array` would return
    mock_outcome_1 = MagicMock(spec=Outcome, Id=10, Name="Invoice", is_download=True)
    mock_outcome_1.outcome_type.Name = "PDF"

    mock_instance_1 = MagicMock(spec=OutcomeInstance, Id=101)
    context_1 = {"client": "A"}

    # # Mock the `build_outcome_instance_array` method to return a predictable list
    # processor.build_outcome_instance_array = MagicMock(
    #     return_value=[
    #         {
    #             "outcome": mock_outcome_1,
    #             "instance": mock_instance_1,
    #             "context": context_1,
    #         }
    #     ]
    # )
    with patch.object(
        processor,
        "build_outcome_instance_array",
        return_value=[
            {
                "outcome": mock_outcome_1,
                "instance": mock_instance_1,
                "context": context_1,
            }
        ],
    ) as _:
        # Mock the service that the factory will create
        mock_storage = MagicMock()
        mock_storage.path.name = "rendered_file.pdf"

        # Create the main service mock and attach the storage mock to the correct attribute
        mock_service = MagicMock(spec=OutcomeService, output_storage_service=mock_storage)

        mock_outcome_service_factory.create.return_value = mock_service

        # Other inputs for the process method
        mock_workflow_instance = MagicMock(spec=WorkflowInstance, Id=1)
        upload_mapping = {"Invoice": "/path/to/invoice_template.docx"}
        download_dir = Path("/tmp/downloads")

        # 2. ACT
        processor.process(
            outcomes=[mock_outcome_1],
            contexts=[context_1],
            workflow_instance=mock_workflow_instance,
            upload_mapping=upload_mapping,
            download_dir=download_dir,
        )

        # 3. ASSERT
        # Verify the factory was called correctly
        mock_outcome_service_factory.create.assert_called_once_with(
            outcome=mock_outcome_1,
            download_dir=download_dir,
            template_uploaded_filename="/path/to/invoice_template.docx",
        )

        # Verify the service was used correctly
        mock_service.render.assert_called_once_with(data=context_1)
        mock_service.save.assert_called_once()

        # Verify the database state was updated
        mock_manager.outcome_instances.set_complete.assert_called_once_with(outcome_instance_id=101)
        mock_manager.outcome_instances.set_rendered_name.assert_called_once_with(
            outcome_instance_id=101, rendered_name="rendered_file.pdf"
        )
        # ANY is used because we don't know how many times it might be called
        mock_manager.commit.assert_called_with()


def test_downloads_exist(mock_outcome_service_factory, mock_manager):
    """Test the downloads_exist helper method."""
    processor = OutcomeProcessor(
        outcome_service_factory=mock_outcome_service_factory, manager=mock_manager
    )

    # Case 1: Downloads exist
    outcomes_with_downloads = [
        MagicMock(spec=Outcome, DownloadName="file1.pdf"),
        MagicMock(spec=Outcome, DownloadName=None),
    ]
    assert processor.downloads_exist(outcomes=outcomes_with_downloads) is True

    # Case 2: No downloads
    outcomes_without_downloads = [
        MagicMock(spec=Outcome, DownloadName=None),
        MagicMock(spec=Outcome, DownloadName=None),
    ]
    assert processor.downloads_exist(outcomes=outcomes_without_downloads) is False

    # Case 3: Empty list
    assert processor.downloads_exist(outcomes=[]) is False
