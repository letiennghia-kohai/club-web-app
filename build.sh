#!/usr/bin/env bash
# Build script for Render.com
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
flask db upgrade

echo "Seeding initial data (if needed)..."
flask seed-db || true  # Ignore error if data already exists

echo "Build completed successfully!"
