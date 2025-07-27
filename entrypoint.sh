#!/usr/bin/env sh
set -e

echo "Starting FastAPI app..."

alembic upgrade head

exec "$@"
