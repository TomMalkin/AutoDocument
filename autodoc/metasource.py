"""Define metasources, such as MetaDatabase, for user supplied database objects."""

from sqlalchemy import VARCHAR, bindparam, create_engine, text

from autodoc.containers import Record, RecordScalar, RecordSet
from autodoc.data.tables import DatabaseMetaSource


class MetaDatabase:
    """A User supplied database."""

    def __init__(self, database: DatabaseMetaSource):
        """Initialise a metadatabase from details in the MetaDatabaseSource table."""
        self.database = database
        self.engine = create_engine(self.database.ConnectionString)

    def check_connection(self) -> bool:
        """Check if a connection to the database can be established."""
        connection = None
        try:
            connection = self.engine.connect()
            return True
        except Exception:
            return False
        finally:
            if connection:
                connection.close()

    def recordset(self, sql: str, params: dict | None = None) -> RecordSet:
        """Create a recordset."""
        headings, data = self.get_data(sql, params)
        return RecordSet(headings, data)

    def record(self, sql: str, params: dict | None = None) -> Record:
        """Create a recordset."""
        headings, data = self.get_data(sql, params)
        return Record(headings, data)

    def record_scalar(self, sql: str, params: dict | None = None) -> RecordScalar:
        """Create a recordset."""
        headings, data = self.get_data(sql, params)
        return RecordScalar(headings, data)

    def execute_sql(self, sql, params=None):
        """Execute :sql: on this connection with named :params:."""
        bound_sql = bind_sql(sql, params)

        connection = self.engine.connect()
        transaction = connection.begin()

        # execute the query, and rollback on error
        try:
            connection.execute(bound_sql)
            transaction.commit()

        except Exception as exception:
            transaction.rollback()
            raise exception

        finally:
            connection.close()

    def get_data(self, sql, params=None):
        """
        Execute <sql> on <con>, with named <params>.

        Return (headings, data)
        """
        # bind the named parameters.
        bound_sql = bind_sql(sql, params)

        # start the connection.
        connection = self.engine.connect()
        transaction = connection.begin()

        # get the results from the query.
        result = connection.execute(bound_sql)
        data = result.fetchall()
        headings = list(result.keys())

        # commit and close the connection
        transaction.commit()
        connection.close()

        return headings, data


def bind_sql(sql, params):
    """Bind parameters to a SQL query."""
    bound_sql = text(sql)

    if params:
        for key, value in params.items():
            # If the type of the value of the parameter is str, then we use
            # the VARCHAR object with no maximum, else use the default Type
            type_ = VARCHAR(None) if isinstance(value, str) else None
            param = bindparam(key=key, value=value, type_=type_)
            bound_sql = bound_sql.bindparams(param)

    return bound_sql
