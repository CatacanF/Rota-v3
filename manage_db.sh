#!/bin/bash
# Script to manage database migrations

echo "🚀 Running Database Migrations..."

# 1. Create a new migration revision
docker-compose exec api alembic revision --autogenerate -m "Auto-generated migration"

# 2. Apply the migration
docker-compose exec api alembic upgrade head

echo "✅ Database updated successfully!"
