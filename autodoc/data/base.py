"""Create the base importable from multiple places with a repr mixin."""

from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base


class ReprMixin:
    """Mixin that provides a ``__repr__`` for SQLAlchemy ORM models."""

    def __repr__(self) -> str:
        """Return a string representation of the model instance."""
        mapper = inspect(self.__class__)
        cols = {c.key: getattr(self, c.key) for c in mapper.columns}
        vals = ", ".join(f"{k}={v!r}" for k, v in cols.items())
        return f"{self.__class__.__name__}({vals})"


Base = declarative_base(cls=ReprMixin)
