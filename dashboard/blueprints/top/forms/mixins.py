"""Define common mixins for forms."""

from wtforms import StringField


class FileAccessorMixin:
    """Mixin class for when the dynamic file accessor snippet is used."""

    bucket = StringField("Bucket")
    location = StringField("Location")
    name = StringField("Name")


class OutputFileAccessorMixin:
    """Mixin class for when the dynamic file accessor snippet is used."""

    output_bucket = StringField("Output Bucket")
    output_location = StringField("Output Location")

class DownloadAccessorMixin:
    """Mixin class for downloads."""

    download_name = StringField("Output Name:")

