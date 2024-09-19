"""Define data containers returned from a database."""

from loguru import logger

class RecordSet:
    """Represents a data container with 1 or more fields and 1 or more rows."""

    def __init__(self, columns, data):
        """Create the container with headings and data."""
        self.headings = columns
        self.data = [dict(zip(columns, row)) for row in data]

    def __bool__(self):
        """Return if this container has data."""
        return self.data is not None

    def column(self, heading):
        """Return a list of data for a particular heading."""
        if heading not in self.headings:
            return []

        return [record[heading] for record in self.data or []]


class Record:
    """
    Represents a data container with 1+ fields but only a single row.

    If multiple rows are returned, only the first is kept.
    """

    def __init__(self, columns, data):
        """Initialize the class with headings and data."""
        logger.debug(f"initialising Record with {columns=} and {data=}")
        self.headings = columns
        self.data = {}

        if isinstance(data, list):
            data = data[0]

        if data:
            self.data = dict(zip(columns, data))

        logger.debug(f"final data is {self.data=}")

    def __bool__(self):
        """Return if this record has data."""
        return bool(self.data)


class RecordScalar:
    """
    Represents a data container with 1 field and only a single row.

    In other words, a single value returned from the database. If multiple headings or rows
    are returned, then only the first heading and first row are kept.

    Truthiness for a scalar is slightly more complicated than RecordSet and Record objects, as
    there are 4 possiblities when attempting to get a scalar datum from a database:
     - No data returned
     - The data point was Null (None)
     - The data returned equates to False: like 0 or an empty string
     - the data returned equates to True: like 1 or a non-empty string

    The truthiness is set to the answer to the question: 'Was any value, even null, returned from
    the database?'.
    """

    def __init__(self, headings, data):
        """Initialize the class with headings and data."""
        # Only keep the first heading
        self.heading = headings[0]

        # Only keep None or the first value of data.
        if data:
            self.is_data_returned = True
            self._datum = data[0][0]
        else:
            self.is_data_returned = False
            self._datum = None

    def __bool__(self):
        """Was a value, even null, returned from the database?."""
        return self.is_data_returned

    def sdatum(self, default=None):
        """
        Return the datum with a default value if the record doesn't exist.

        sdatum stands for Safe Datum, providing a default value instead of
        raising an error if the record doesn't exist.
        """
        if not self:
            return default
        return self._datum

    def datum(self):
        """If you know the datum exists and isn't None, use this."""
        if not self._datum:
            raise

        return self._datum
