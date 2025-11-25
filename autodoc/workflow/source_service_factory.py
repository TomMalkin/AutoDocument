"""Handle loading of source services."""

from typing import Optional

from autodoc.data.tables import Source
from autodoc.source import source_service_map
from autodoc.source.source import SourceService as SourceServiceInterface


class SourceServiceFactory:
    """The source service factory."""

    def create(self, source: Source, uploaded_filename: Optional[str]) -> SourceServiceInterface:
        """Create and return a source service instance."""
        source_type_name = source.source_type.Name
        service_class = source_service_map.get(source_type_name)

        if not service_class:
            raise ValueError(f"Unknown source type: {source_type_name}")

        return service_class(source=source, uploaded_filename=uploaded_filename)
