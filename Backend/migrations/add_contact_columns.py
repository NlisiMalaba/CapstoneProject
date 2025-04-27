"""Add contact columns migration

This script runs directly to add contact_email and emergency_contact columns to the user_profiles table.
"""
from app.main import create_app
from app.database import db
import sqlite3
import os

def run_migration():
    app = create_app('development')
    
    with app.app_context():
        # Get database path from app config
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            
            # Connect to SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(user_profiles)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
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
        else:
            print(f"Database is not SQLite, please update database manually. URI: {db_uri}")

if __name__ == "__main__":
    run_migration() 