"""
Database migration script to add wrong_minigame column to assignments table
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
    
    # Check if wrong_minigame column already exists in assignments
    cursor.execute("PRAGMA table_info(assignments)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'wrong_minigame' not in columns:
        print("Adding 'wrong_minigame' column to assignments table...")
        cursor.execute("ALTER TABLE assignments ADD COLUMN wrong_minigame VARCHAR(32) DEFAULT 'randomized'")
        conn.commit()
        print("✓ Successfully added 'wrong_minigame' column!")
    else:
        print("'wrong_minigame' column already exists. No migration needed.")
    
    # Update any existing assignments without wrong_minigame to 'randomized'
    cursor.execute("UPDATE assignments SET wrong_minigame = 'randomized' WHERE wrong_minigame IS NULL OR wrong_minigame = ''")
    affected_rows = cursor.rowcount
    conn.commit()
    
    if affected_rows > 0:
        print(f"✓ Updated {affected_rows} existing assignments to 'randomized' wrong_minigame")
    
    print("\nMigration completed successfully!")
    
    # Show summary
    cursor.execute("SELECT wrong_minigame, COUNT(*) FROM assignments GROUP BY wrong_minigame")
    results = cursor.fetchall()
    print("\nCurrent wrong_minigame distribution:")
    for wrong_minigame, count in results:
        print(f"  {wrong_minigame}: {count} assignments")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"Error during migration: {e}")