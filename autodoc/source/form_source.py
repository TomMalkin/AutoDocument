"""User input sources. Heavily based on WTForms."""

from autodoc.source.source import Source


class FormSource(Source):
    """Form data Source."""

    def __init__(self, source_id: int, fields: list) -> None:
        """Initialise the form source by getting all the form fields."""
        self.source_id = source_id
        self.fields = fields
        self.is_multi_record = False

    def receive_data(self, data: dict) -> None:
        """Receive data externally and set to this object."""
        self.data = data
