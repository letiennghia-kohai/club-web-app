"""
Quick script to create tag tables manually if migration fails
Run this with: venv\Scripts\python.exe create_tags_table.py
"""
from app import create_app, db
from app.models.tag import Tag, post_tags

print("Creating tag tables...")

app = create_app()
with app.app_context():
    # Create tags and post_tags tables
    db.create_all()
    print("✓ Tables created successfully!")
    
    # Verify
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'tags' in tables:
        print("✓ 'tags' table created")
    if 'post_tags' in tables:
        print("✓ 'post_tags' table created")
    
    print(f"\nAll tables: {tables}")
