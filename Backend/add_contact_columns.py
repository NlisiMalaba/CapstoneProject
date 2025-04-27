"""Add contact columns to user_profiles table

This script directly connects to the SQLite database to add the missing columns.
"""
import sqlite3
import os
import glob

def find_sqlite_db():
    """Find SQLite database file in the project"""
    # Check common locations
    db_paths = [
        "instance/app.db",
        "instance/database.db",
        "instance/app.sqlite",
        "app.db",
        "database.db"
    ]
    
    # Try each path
    for path in db_paths:
        if os.path.exists(path):
            return path
    
    # Search for .db files in common directories
    for ext in ["*.db", "*.sqlite", "*.sqlite3"]:
        for db_file in glob.glob(f"instance/{ext}") + glob.glob(ext):
            return db_file
    
    return None

def run_migration():
    db_path = find_sqlite_db()
    
    if not db_path:
        print("Error: Could not find SQLite database file.")
        return
    
    print(f"Found database at: {db_path}")
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'")
        if not cursor.fetchone():
            print("Error: user_profiles table does not exist.")
            conn.close()
            return
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Existing columns: {column_names}")
        
        # Add columns if they don't exist
        if 'contact_email' not in column_names:
            print("Adding contact_email column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN contact_email VARCHAR(100)")
        
        if 'emergency_contact' not in column_names:
            print("Adding emergency_contact column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN emergency_contact VARCHAR(200)")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Migration completed successfully!")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_migration() 