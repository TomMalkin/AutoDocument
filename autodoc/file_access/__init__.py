"""Expose File Access classes."""

from .linux import LinuxFileAccess as LinuxFileAccess
from .windows import WindowsFileAccess as WindowsFileAccess
from .file_access import FileAccess as FileAccess
from .s3 import S3FileAccess
from .sharepoint import SharePointSiteFileAccess
from typing import Type

class_map = {
    "Windows Share": WindowsFileAccess,
    "Linux Share": LinuxFileAccess,
    "S3": S3FileAccess,
    "SharePoint": SharePointSiteFileAccess,
}


def get_file_access_class(name) -> Type[FileAccess]:
    """Return the class based on the name."""
    return class_map[name]
