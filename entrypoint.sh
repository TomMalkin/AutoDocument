#!/bin/bash
set -e

# create or upgrade database
alembic upgrade head

# seed type data
flask init-db

# Execute the command passed to the script
exec "$@"
