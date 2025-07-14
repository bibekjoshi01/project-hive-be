#!/usr/bin/env sh
set -e

DB_HOST=${DB_HOST:-db}

echo "Waiting for db ($DB_HOST)…"
while ! nc -z "$DB_HOST" 5432; do
  sleep 1
done
echo "Database is ready!"

alembic upgrade head

exec "$@"
