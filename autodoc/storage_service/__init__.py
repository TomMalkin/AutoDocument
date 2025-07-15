"""Expose Storage Service classes."""

from autodoc.data.tables import FileTemplate

from .base import StorageService
from .dropbox import DropboxStorageService
from .linux import LinuxStorageService
from .s3 import S3StorageService
from .sharepoint import SharePointSiteStorageService
from .windows import WindowsStorageService

storage_service_class_map = {
    "Windows Share": WindowsStorageService,
    "Linux Share": LinuxStorageService,
    "S3": S3StorageService,
    "SharePoint": SharePointSiteStorageService,
    "Dropbox": DropboxStorageService,
}


def get_storage_service(file_template: FileTemplate) -> StorageService:
    """For a given file template, return a FileTemplateService."""
    storage_type_name = file_template.storage_instance.storage_type.Name
    storage_service_class = storage_service_class_map.get(storage_type_name)

    if not storage_service_class:
        raise ValueError(f"Unknown Storage Service: {storage_type_name}")

    storage_service = storage_service_class(
        root=file_template.get_root(),
        relative=file_template.Location,
        url=file_template.storage_instance.URL,
        username=file_template.storage_instance.Username,
        password=file_template.storage_instance.Password,
    )

    return storage_service
