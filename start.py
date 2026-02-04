#!/usr/bin/env python
"""Startup script for Railway deployment"""
import os
import subprocess
import sys

print("=== Starting Railway Deployment ===")

# Initialize database if needed
print("Checking database...")
try:
    from app import create_app, db
    from app.utils.seed import seed_data # This import might not be needed if seed_data is moved into reset_database_if_needed or removed.
    
    app = create_app()
    with app.app_context():
        # Check if database reset is requested
        reset_database_if_needed()
        
        # Initialize database (create tables if they don't exist)
        init_database()

        # Original seed_data call, kept for compatibility if not fully replaced by reset_database_if_needed
        try:
            seed_data()
            print("✅ Initial data seeded")
        except Exception as e:
            print(f"ℹ️  Seed skipped (data may already exist): {e}")
            
except Exception as e:
    print(f"⚠️  Database check/init failed: {e}")
    print("Will try to start anyway...")

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
