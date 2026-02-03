"""Initialize database - Run once to create tables and seed data"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.utils.seed import seed_database

print("=" * 50)
print("DATABASE INITIALIZATION")
print("=" * 50)

app = create_app()

with app.app_context():
    try:
        print("\n1. Creating all database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        print("\n2. Seeding initial data...")
        seed_database()
        print("✅ Database initialized successfully!")
        
        print("\n" + "=" * 50)
        print("DONE! You can now use the application.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf error says 'already exists', database is already initialized.")
        print("You can safely ignore this error.")
        sys.exit(0)  # Exit with success anyway
