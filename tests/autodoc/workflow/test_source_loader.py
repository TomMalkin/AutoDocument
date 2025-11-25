"""Test the SourceLoader class."""

from unittest.mock import MagicMock, call

from autodoc.data.tables import Source, WorkflowInstance
from autodoc.source import SourceService
from autodoc.workflow.source_loader import SourceLoader


def test_builds_correctly(mock_source_service_factory, mock_manager):
    """Test that the SourceLoader builds correctly."""
    source_loader = SourceLoader(
        source_service_factory=mock_source_service_factory, manager=mock_manager
    )

    assert source_loader.factory is mock_source_service_factory
    assert source_loader.manager is mock_manager


def test_check_succeeds(mock_source_service_factory, mock_manager):
    """Test the check method of SourceLoader when all sources are valid."""
    # Create mocked Source objects.
    mock_source_1 = MagicMock(spec=Source)
    mock_source_1.Name = "Client Data"
    mock_source_1.Id = 1

    mock_source_2 = MagicMock(spec=Source)
    mock_source_2.Name = "Product List"
    mock_source_2.Id = 2

    sources_list = [mock_source_1, mock_source_2]
    upload_mapping = {"Client Data": "/path/to/client.csv"}

    # Create mocked Services that are succeeding.
    mock_service_1 = MagicMock(spec=SourceService)
    mock_service_1.check.return_value = (True, None)

    mock_service_2 = MagicMock(spec=SourceService)
    mock_service_2.check.return_value = (True, None)

    # factory.create will return the services in order.
    mock_source_service_factory.create.side_effect = [mock_service_1, mock_service_2]

    source_loader = SourceLoader(
        source_service_factory=mock_source_service_factory, manager=mock_manager
    )

    is_ok, reasons = source_loader.check(sources=sources_list, upload_mapping=upload_mapping)

    assert is_ok is True
    assert reasons == []

    expected_calls = [
        call(mock_source_1, "/path/to/client.csv"),  # Found in upload_mapping
        call(mock_source_2, None),  # Not in upload_mapping
    ]

    mock_source_service_factory.create.assert_has_calls(expected_calls)
    assert mock_source_service_factory.create.call_count == 2

    # Verify that the `check` method was called on each service mock.
    mock_service_1.check.assert_called_once()
    mock_service_2.check.assert_called_once()


def test_check_fails(mock_source_service_factory, mock_manager):
    """Test the check method when one of the sources is invalid."""
    # 1. ARRANGE
    mock_source_1 = MagicMock(spec=Source)
    mock_source_1.Name = "Valid Source"
    mock_source_1.Id = 1

    mock_source_2 = MagicMock(spec=Source)
    mock_source_2.Name = "Invalid Source"
    mock_source_2.Id = 2

    sources_list = [mock_source_1, mock_source_2]
    upload_mapping = {}

    # This time, one of the services returns a failure tuple.
    mock_service_1 = MagicMock(spec=SourceService)
    mock_service_1.check.return_value = (True, None)

    mock_service_2 = MagicMock(spec=SourceService)
    mock_service_2.check.return_value = (False, "Database connection failed")

    mock_source_service_factory.create.side_effect = [mock_service_1, mock_service_2]

    source_loader = SourceLoader(
        source_service_factory=mock_source_service_factory, manager=mock_manager
    )

    # 2. ACT
    is_ok, reasons = source_loader.check(sources=sources_list, upload_mapping=upload_mapping)

    # 3. ASSERT

    # Check that the return value correctly reflects the failure.
    assert is_ok is False
    assert reasons == ["Database connection failed"]

    mock_source_service_factory.create.assert_has_calls(
        [call(mock_source_1, None), call(mock_source_2, None)]
    )
    mock_service_1.check.assert_called_once()
    mock_service_2.check.assert_called_once()


def test_source_loader_build_contexts_with_no_initial(mock_source_service_factory, mock_manager):
    """Test the build contexts method."""
    # 1. ARRANGE

    # Sources in order:
    # 1) Single record,
    # 2) multi-record to field,
    # 3) multi-record to splitter,
    # 4) another single record,
    # 5) multi-record to splitter

    mock_source_1 = MagicMock(spec=Source)
    mock_source_1.Name = "Single Record 1"
    mock_source_1.Id = 1

    mock_source_2 = MagicMock(spec=Source)
    mock_source_2.Name = "Multi Record to Field"
    mock_source_2.Splitter = False
    mock_source_2.FieldName = "src2field"
    mock_source_2.Id = 2

    mock_source_3 = MagicMock(spec=Source)
    mock_source_3.Name = "Multi Record to Splitter 1"
    mock_source_3.Splitter = True
    mock_source_3.Id = 3

    mock_source_4 = MagicMock(spec=Source)
    mock_source_4.Name = "Single Record 2"
    mock_source_4.Id = 4

    mock_source_5 = MagicMock(spec=Source)
    mock_source_5.Name = "Multi Record to Splitter 2"
    mock_source_5.Splitter = True
    mock_source_5.Id = 5

    mock_sources_list = [mock_source_1, mock_source_2, mock_source_3, mock_source_4, mock_source_5]

    # Single Record 1
    mock_service_1 = MagicMock(spec=SourceService)
    mock_service_1.is_multi_record = False
    mock_service_1.data = {"some": "data", "foo": 1}

    # Multi Record to Field
    mock_service_2 = MagicMock(spec=SourceService)
    mock_service_2.is_multi_record = True
    mock_service_2.data = [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}]

    # splitter 1
    mock_service_3 = MagicMock(spec=SourceService)
    mock_service_3.is_multi_record = True
    mock_service_3.data = [{"split": "one"}, {"split": "two"}]

    # another single record
    mock_service_4 = MagicMock(spec=SourceService)
    mock_service_4.is_multi_record = False
    mock_service_4.data = {"insert": "here"}

    # splitter 2
    mock_service_5 = MagicMock(spec=SourceService)
    mock_service_5.is_multi_record = True
    mock_service_5.data = [{"another split": "A"}, {"another split": "B"}]

    mock_service_1.source = mock_source_1
    mock_service_2.source = mock_source_2
    mock_service_3.source = mock_source_3
    mock_service_4.source = mock_source_4
    mock_service_5.source = mock_source_5

    expected_context = [
        {
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
            "another split": "A",
        },
        {
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
            "another split": "B",
        },
        {
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "two",
            "insert": "here",
            "another split": "A",
        },
        {
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "two",
            "insert": "here",
            "another split": "B",
        },
    ]

    mock_services = [
        mock_service_1,
        mock_service_2,
        mock_service_3,
        mock_service_4,
        mock_service_5,
    ]

    mock_source_service_factory.create.side_effect = mock_services
    source_loader = SourceLoader(
        source_service_factory=mock_source_service_factory, manager=mock_manager
    )

    # 2. ACT
    mock_instance = MagicMock(spec=WorkflowInstance)
    contexts = source_loader.build_contexts(
        sources=mock_sources_list,
        workflow_instance=mock_instance,
        initial_data={},
        upload_mapping={},
    )

    # 3. ASSERT
    assert contexts == expected_context

    mock_service_1.load_data.assert_called_with(current_data={})
    mock_service_2.load_data.assert_called_with(current_data={"some": "data", "foo": 1})
    mock_service_3.load_data.assert_called_with(
        current_data={
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
        }
    )
    mock_service_4.load_data.assert_any_call(
        current_data={
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
        }
    )
    mock_service_5.load_data.assert_any_call(
        current_data={
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
        }
    )

    assert mock_service_1.load_data.call_count == 1
    assert mock_service_2.load_data.call_count == 1
    assert mock_service_3.load_data.call_count == 1
    assert mock_service_4.load_data.call_count == 2
    assert mock_service_5.load_data.call_count == 2


def test_source_loader_build_contexts_with_initial(mock_source_service_factory, mock_manager):
    """Test the build contexts method."""
    # 1. ARRANGE

    # Sources in order:
    # 1) Single record,
    # 2) multi-record to field,
    # 3) multi-record to splitter,
    # 4) another single record,
    # 5) multi-record to splitter

    initial_data = {"initial": "value"}

    mock_source_1 = MagicMock(spec=Source)
    mock_source_1.Name = "Single Record 1"
    mock_source_1.Id = 1

    mock_source_2 = MagicMock(spec=Source)
    mock_source_2.Name = "Multi Record to Field"
    mock_source_2.Splitter = False
    mock_source_2.FieldName = "src2field"
    mock_source_2.Id = 2

    mock_source_3 = MagicMock(spec=Source)
    mock_source_3.Name = "Multi Record to Splitter 1"
    mock_source_3.Splitter = True
    mock_source_3.Id = 3

    mock_source_4 = MagicMock(spec=Source)
    mock_source_4.Name = "Single Record 2"
    mock_source_4.Id = 4

    mock_source_5 = MagicMock(spec=Source)
    mock_source_5.Name = "Multi Record to Splitter 2"
    mock_source_5.Splitter = True
    mock_source_5.Id = 5

    mock_sources_list = [mock_source_1, mock_source_2, mock_source_3, mock_source_4, mock_source_5]

    # Single Record 1
    mock_service_1 = MagicMock(spec=SourceService)
    mock_service_1.is_multi_record = False
    mock_service_1.data = {"some": "data", "foo": 1}

    # Multi Record to Field
    mock_service_2 = MagicMock(spec=SourceService)
    mock_service_2.is_multi_record = True
    mock_service_2.data = [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}]

    # splitter 1
    mock_service_3 = MagicMock(spec=SourceService)
    mock_service_3.is_multi_record = True
    mock_service_3.data = [{"split": "one"}, {"split": "two"}]

    # another single record
    mock_service_4 = MagicMock(spec=SourceService)
    mock_service_4.is_multi_record = False
    mock_service_4.data = {"insert": "here"}

    # splitter 2
    mock_service_5 = MagicMock(spec=SourceService)
    mock_service_5.is_multi_record = True
    mock_service_5.data = [{"another split": "A"}, {"another split": "B"}]

    mock_service_1.source = mock_source_1
    mock_service_2.source = mock_source_2
    mock_service_3.source = mock_source_3
    mock_service_4.source = mock_source_4
    mock_service_5.source = mock_source_5

    expected_context = [
        {
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
            "another split": "A",
        },
        {
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
            "another split": "B",
        },
        {
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "two",
            "insert": "here",
            "another split": "A",
        },
        {
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "two",
            "insert": "here",
            "another split": "B",
        },
    ]

    mock_services = [
        mock_service_1,
        mock_service_2,
        mock_service_3,
        mock_service_4,
        mock_service_5,
    ]

    mock_source_service_factory.create.side_effect = mock_services
    source_loader = SourceLoader(
        source_service_factory=mock_source_service_factory, manager=mock_manager
    )

    # 2. ACT
    mock_instance = MagicMock(spec=WorkflowInstance)
    contexts = source_loader.build_contexts(
        sources=mock_sources_list,
        workflow_instance=mock_instance,
        initial_data=initial_data,
        upload_mapping={},
    )

    # 3. ASSERT
    assert contexts == expected_context

    mock_service_1.load_data.assert_called_with(current_data={"initial": "value"})
    mock_service_2.load_data.assert_called_with(
        current_data={"initial": "value", "some": "data", "foo": 1}
    )
    mock_service_3.load_data.assert_called_with(
        current_data={
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
        }
    )
    mock_service_4.load_data.assert_any_call(
        current_data={
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
        }
    )
    mock_service_5.load_data.assert_any_call(
        current_data={
            "initial": "value",
            "some": "data",
            "foo": 1,
            "src2field": [{"client_name": "John", "age": 35}, {"client_name": "alice", "age": 24}],
            "split": "one",
            "insert": "here",
        }
    )

    assert mock_service_1.load_data.call_count == 1
    assert mock_service_2.load_data.call_count == 1
    assert mock_service_3.load_data.call_count == 1
    assert mock_service_4.load_data.call_count == 2
    assert mock_service_5.load_data.call_count == 2
