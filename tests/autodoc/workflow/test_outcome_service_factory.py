"""Test the OutcomeServiceFactory."""

from unittest.mock import MagicMock

import pytest

from autodoc.data.tables import Outcome, OutcomeType
from autodoc.outcome.word_outcome import WordOutcomeService
from autodoc.workflow.outcome_service_factory import OutcomeServiceFactory


def test_create_with_known_outcome(test_download_dir):
    """Test if the factory will create the correct service with a given outcome."""
    # 1. ARRANGE
    mock_outcome = MagicMock(spec=Outcome)

    mock_outcome.outcome_type = MagicMock(spec=OutcomeType)
    mock_outcome.outcome_type.Name = "Microsoft Word"

    outcome_service_factory = OutcomeServiceFactory()

    # 2. ACT
    outcome_service = outcome_service_factory.create(
        outcome=mock_outcome, download_dir=test_download_dir, template_uploaded_filename=None
    )

    # 3. ASSERT
    assert isinstance(outcome_service, WordOutcomeService)


def test_create_with_unknown_outcome(test_download_dir):
    """Test that a ValueError is raised if an unknown outcome is created."""
    # 1. ARRANGE
    mock_outcome = MagicMock(spec=Outcome)

    mock_outcome.outcome_type = MagicMock(spec=OutcomeType)
    mock_outcome.outcome_type.Name = "Unknown Outcome Type"

    outcome_service_factory = OutcomeServiceFactory()

    # 2. ACT and 3. ASSERT
    with pytest.raises(ValueError, match="Unknown outcome type: Unknown Outcome Type"):
        outcome_service_factory.create(
            outcome=mock_outcome, download_dir=test_download_dir, template_uploaded_filename=None
        )
