"""Define Services."""

from typing import Optional


from .repositories import StorageTypeRepository, StorageInstanceRepository


class StorageService:
    """Manage more complicated joins for Storage actions."""

    def __init__(self, type_repo: StorageTypeRepository, instance_repo: StorageInstanceRepository):
        """Create the Service with the instance and type repos."""
        self.type_repo = type_repo
        self.instance_repo = instance_repo

    def add_instance_with_type(
        self,
        storage_type_name: str,
        local_path: Optional[str] = None,
        remote_path: Optional[str] = None,
        top_level: Optional[str] = None,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Add a Storage Instance and link it to a Storage Type."""
        storage_type = self.type_repo.get_by_name(name=storage_type_name)

        if not storage_type:
            raise ValueError(f"Unknown Storage Type: {storage_type}")

        storage_type_id = storage_type.Id

        if not storage_type_id:
            return None

        return self.instance_repo.add(
            storage_type=storage_type,
            local_path=local_path,
            remote_path=remote_path,
            top_level=top_level,
            url=url,
            username=username,
            password=password,
        )
