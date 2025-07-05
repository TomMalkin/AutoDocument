"""Models for the top level."""

from typing import Optional

from autodoc.data.manager import DatabaseManager


def get_optional_new_file_template_id(
    manager: DatabaseManager,
    storage_instance_id: int,
    location: Optional[str],
    bucket: Optional[str],
) -> Optional[int]:
    """If the storage instance id is valid, then create a new file_template and return it's Id."""
    if not file_template_required(storage_instance_id):
        return None

    file_template_id = manager.file_templates.add(
        storage_instance_id=storage_instance_id,
        location=location,
        bucket=bucket,
    ).Id

    return file_template_id


def file_template_required(storage_instance_id: Optional[int]) -> bool:
    """Return if a file template is required based on the selected storage instance."""
    return storage_instance_id not in (None, -1)
