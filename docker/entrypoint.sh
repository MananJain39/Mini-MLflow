#!/bin/bash
set -e

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start server
echo "Starting Uvicorn..."
exec python -m uvicorn mini_mlflow.server.main:app --host 0.0.0.0 --port 8000
