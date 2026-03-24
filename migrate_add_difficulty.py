"""
Database migration script to add difficulty column to questions table
Run this script to update your existing database
"""
import sqlite3
import os

# Get the database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "school.db")

print(f"Migrating database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if difficulty column already exists
    cursor.execute("PRAGMA table_info(questions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'difficulty' not in columns:
        print("Adding 'difficulty' column to questions table...")
        cursor.execute("ALTER TABLE questions ADD COLUMN difficulty VARCHAR(10) DEFAULT 'easy'")
        conn.commit()
        print("✓ Successfully added 'difficulty' column!")
    else:
        print("'difficulty' column already exists. No migration needed.")
    
    # Update any existing questions without difficulty to 'easy'
    cursor.execute("UPDATE questions SET difficulty = 'easy' WHERE difficulty IS NULL OR difficulty = ''")
    affected_rows = cursor.rowcount
    conn.commit()
    
    if affected_rows > 0:
        print(f"✓ Updated {affected_rows} existing questions to 'easy' difficulty")
    
    print("\nMigration completed successfully!")
    
    # Show summary
    cursor.execute("SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty")
    results = cursor.fetchall()
    print("\nCurrent difficulty distribution:")
    for difficulty, count in results:
        print(f"  {difficulty}: {count} questions")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"Error during migration: {e}")
    if conn:
        conn.rollback()
        conn.close()
except Exception as e:
    print(f"Unexpected error: {e}")
    if conn:
        conn.close()
