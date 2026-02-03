#!/usr/bin/env python
"""Startup script for Railway deployment"""
import os
import subprocess
import sys

print("=== Starting Railway Deployment ===")

# Run migrations
print("Running database migrations...")
result = subprocess.run([sys.executable, "-m", "flask", "db", "upgrade"], capture_output=False)
if result.returncode != 0:
    print("Warning: Migration failed, but continuing...")

# Seed database
print("Seeding database...")
result = subprocess.run([sys.executable, "-m", "flask", "seed-db"], capture_output=False)
if result.returncode != 0:
    print("Warning: Seeding failed (data may already exist), continuing...")

# Start Gunicorn
print("Starting Gunicorn...")
port = os.environ.get("PORT", "8000")
subprocess.run([
    "gunicorn",
    "--bind", f"0.0.0.0:{port}",
    "--workers", "4",
    "--timeout", "120",
    "wsgi:application"
])
