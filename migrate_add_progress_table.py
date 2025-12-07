"""
Database migration script to add assignment_progress table for Unity app
Run this script to add progress tracking support
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
    
    # Check if assignment_progress table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assignment_progress'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("Creating 'assignment_progress' table...")
        cursor.execute("""
            CREATE TABLE assignment_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                assignment_id INTEGER NOT NULL,
                current_question_index INTEGER DEFAULT 0,
                answers_json TEXT,
                locked_questions_json TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("✓ Successfully created 'assignment_progress' table!")
    else:
        print("'assignment_progress' table already exists. No migration needed.")
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_progress_student_assignment 
        ON assignment_progress(student_id, assignment_id)
    """)
    conn.commit()
    print("✓ Created index on (student_id, assignment_id)")
    
    print("\nMigration completed successfully!")
    
    # Show summary
    cursor.execute("SELECT COUNT(*) FROM assignment_progress")
    count = cursor.fetchone()[0]
    print(f"\nCurrent progress records: {count}")
    
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
