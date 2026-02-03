#!/bin/bash
# Entrypoint script for Railway deployment

# Debug: Print environment variables (remove after testing)
echo "=== Environment Check ==="
echo "PORT: ${PORT:-not set}"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..." # Only show first 50 chars for security
echo "FLASK_ENV: ${FLASK_ENV:-not set}"

# Get PORT from environment, default to 8000
PORT=${PORT:-8000}

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    exit 1
fi

echo "Starting application on port $PORT..."

# Run Gunicorn with dynamic port
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:application
