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
    from app.utils.seed import seed_data
    
    app = create_app()
    with app.app_context():
        # Try to create tables (will skip if already exist)
        db.create_all()
        print("✅ Database tables ready")
        
        # Try to seed data (will skip if already exists)
        try:
            seed_data()
            print("✅ Initial data seeded")
        except Exception as e:
            print(f"ℹ️  Seed skipped (data may already exist): {e}")
            
except Exception as e:
    print(f"⚠️  Database check failed: {e}")
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
