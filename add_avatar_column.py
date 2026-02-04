"""
Add avatar column to users table manually
"""
import sqlite3
import os

# Find database file
db_path = 'instance/club.db'
if not os.path.exists(db_path):
    db_path = 'instance/app.db'
if not os.path.exists(db_path):
    print('✗ Database file not found!')
    exit(1)

print(f'Using database: {db_path}')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add avatar column
    cursor.execute('ALTER TABLE users ADD COLUMN avatar VARCHAR(255)')
    conn.commit()
    print('✓ Avatar column added successfully')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print('✓ Avatar column already exists')
    else:
        print(f'✗ Error: {e}')
finally:
    conn.close()
