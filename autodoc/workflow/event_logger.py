from typing import Optional


class EventLoggerInterface:
    """Base class for Event Loggers."""

    def write_source_event(
        self,
        instance_id: int,
        source_id: Optional[int],
        source_data: dict,
        source_data_ongoing: dict,
    ) -> None:
        """Write a Source event."""

    def write_outcome_event(self, instance_id: int, outcome_id: int, outcome_location: str) -> None:
        """Write an Outcome event."""
