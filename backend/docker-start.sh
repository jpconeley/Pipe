#!/bin/sh
# Container entrypoint: migrate, optionally load demo data, then serve the API.
set -e

alembic upgrade head
pvf seed-reference
if [ "$PVF_SEED_DEMO" = "1" ]; then
  pvf seed-demo
fi

exec uvicorn pvf.api.main:app --host 0.0.0.0 --port 8000
