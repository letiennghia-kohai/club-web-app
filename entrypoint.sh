#!/bin/bash
# Entrypoint script for Railway deployment

# Get PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "Starting application on port $PORT..."

# Run Gunicorn with dynamic port
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application
