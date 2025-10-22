#!/usr/bin/env sh
set -e

until alembic upgrade head; do
  echo "Waiting for database..."
  sleep 2
done

exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
