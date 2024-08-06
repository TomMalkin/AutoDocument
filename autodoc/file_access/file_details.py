"""Define Template Details Classes."""

from . import get_file_access_class


class TemplateFileDetails:
    """Get the template details from the larger outcome_details."""

    def __init__(self, outcome_details):
        """Initialise."""
        self.root = (
            outcome_details["InputLocalPath"]
            or outcome_details["InputFileBucket"]
            or outcome_details["InputRemotePath"]
        )
        self.relative = outcome_details["InputFileLocation"]
        self.storage_type = outcome_details["InputFileTypeName"]
        self.url = outcome_details["InputURL"]
        self.username = outcome_details["InputUserName"]
        self.password = outcome_details["InputPassword"]

    def get_file_access_class(self):
        """Get the file access class for these details."""
        file_access_class = get_file_access_class(self.storage_type)
        return file_access_class(
            root=self.root,
            relative=self.relative,
            url=self.url,
            username=self.username,
            password=self.password,
        )


class OutputFileDetails:
    """Get the template details from the larger outcome_details."""

    def __init__(self, outcome_details):
        """Initialise."""
        self.root = (
            outcome_details["OutputLocalPath"]
            or outcome_details["OutputFileBucket"]
            or outcome_details["OutputRemotePath"]
        )
        self.relative = outcome_details["OutputFileLocation"]
        self.storage_type = outcome_details["OutputFileTypeName"]
        self.url = outcome_details["OutputURL"]
        self.username = outcome_details["OutputUserName"]
        self.password = outcome_details["OutputPassword"]

    def get_file_access_class(self):
        """Get the file access class for these details."""
        file_access_class = get_file_access_class(self.storage_type)
        return file_access_class(
            root=self.root,
            relative=self.relative,
            url=self.url,
            username=self.username,
            password=self.password,
        )


class SourceFileDetails:
    """Get the template details from the larger outcome_details."""

    def __init__(self, source_details):
        """Initialise."""
        self.root = (
            source_details["LocalPath"] or source_details["Bucket"] or source_details["RemotePath"]
        )
        self.relative = source_details["Location"]
        self.storage_type = source_details["FileAccessTypeName"]
        self.url = source_details["URL"]
        self.username = source_details["Username"]
        self.password = source_details["Password"]

    def get_file_access_class(self):
        """Get the file access class for these details."""
        file_access_class = get_file_access_class(self.storage_type)
        return file_access_class(
            root=self.root,
            relative=self.relative,
            url=self.url,
            username=self.username,
            password=self.password,
        )
