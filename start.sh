#!/bin/bash
# Startup script for Railway

echo "=== Starting Railway Deployment ==="

# Run migrations
echo "Running database migrations..."
python -m flask db upgrade

# Seed initial data (ignore if already exists)
echo "Seeding database..."
python -m flask seed-db || echo "Seed data already exists, skipping..."

# Start application
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application
