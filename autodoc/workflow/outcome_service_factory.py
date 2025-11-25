"""Handle loading of outcome services."""

from pathlib import Path
from typing import Optional

from autodoc.data.tables import Outcome
from autodoc.outcome import outcome_service_map
from autodoc.outcome.outcome import OutcomeService as OutcomeServiceInterface


class OutcomeServiceFactory:
    """The outcome service factory."""

    def create(
        self, outcome: Outcome, download_dir: Optional[Path], template_uploaded_filename: str | None
    ) -> OutcomeServiceInterface:
        """Create and return an outcome service instance."""
        outcome_type_name = outcome.outcome_type.Name
        service_class = outcome_service_map.get(outcome_type_name)

        if not service_class:
            raise ValueError(f"Unknown outcome type: {outcome_type_name}")

        return service_class(
            outcome=outcome,
            download_dir=download_dir,
            template_uploaded_filename=template_uploaded_filename,
        )
