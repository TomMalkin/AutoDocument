"""Test the SourceServiceFactory."""

from unittest.mock import MagicMock

import pytest

from autodoc.data.tables import Source, SourceType
from autodoc.source.csv_source import CSVRecordSourceService
from autodoc.workflow.source_service_factory import SourceServiceFactory


def test_create_with_known_source():
    """Test if the factory will create the correct service with a given source."""
    # 1. ARRANGE
    mock_source = MagicMock(spec=Source)

    mock_source.source_type = MagicMock(spec=SourceType)
    mock_source.source_type.Name = "CSVRecord"

    source_service_factory = SourceServiceFactory()

    # 2. ACT
    source_service = source_service_factory.create(source=mock_source, uploaded_filename=None)

    # 3. ASSERT
    assert isinstance(source_service, CSVRecordSourceService)


def test_create_with_unknown_source():
    """Test that a ValueError is raised if an unknown source is created."""
    # 1. ARRANGE
    mock_source = MagicMock(spec=Source)

    mock_source.source_type = MagicMock(spec=SourceType)
    mock_source.source_type.Name = "Unknown Source Type"

    source_service_factory = SourceServiceFactory()

    # 2. ACT and 3. ASSERT
    with pytest.raises(ValueError, match="Unknown source type: Unknown Source Type"):
        source_service_factory.create(source=mock_source, uploaded_filename=None)
