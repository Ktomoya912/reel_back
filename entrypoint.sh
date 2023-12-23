#!/bin/bash

# DB migration
poetry run python -m api.migrate_cloud_db

echo "Starting server..."

# uvicorn 
poetry run uvicorn api.main:app --host 0.0.0.0
