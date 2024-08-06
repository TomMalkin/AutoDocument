"""Expose function used to initialise items before workflow is accessed."""
from autodoc.db import initialise_database


def pre_run():
    """Initialise autodoc."""
    initialise_database()




