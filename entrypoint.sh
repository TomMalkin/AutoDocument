#!/bin/bash
set -e

flask init-db

# Execute the command passed to the script
exec "$@"
