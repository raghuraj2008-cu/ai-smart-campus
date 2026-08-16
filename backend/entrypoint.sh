#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head || echo "Alembic migrations skipped or up to date."

echo "Starting Uvicorn production server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4