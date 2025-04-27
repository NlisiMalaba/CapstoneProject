"""
Run database migrations directly with SQLAlchemy
"""
import os
import sys
import sqlite3
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# Check for instance database first, then fall back to app.db
if os.path.exists(os.path.join('instance', 'dev.db')):
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///instance/dev.db')
    print(f"Using instance database: {DATABASE_URI}")
else:
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    print(f"Using root database: {DATABASE_URI}")

def run_migrations():
    """Add missing columns to database tables"""
    print(f"Running migrations on database: {DATABASE_URI}")
    
    # Create engine
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()
    
    try:
        # Check if prediction_history table exists
        if 'sqlite' in DATABASE_URI:
            # SQLite approach
            # Connect to SQLite database
            db_path = DATABASE_URI.replace('sqlite:///', '')
            print(f"SQLite DB path: {db_path}")
            
            # Ensure the directory exists if path contains directories
            if os.path.dirname(db_path):
                os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
            sqlite_conn = sqlite3.connect(db_path)
            cursor = sqlite_conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prediction_history'")
            if not cursor.fetchone():
                print("Table prediction_history does not exist. Creating it...")
                
                # First check if patient_data table exists (it's referenced by prediction_history)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patient_data'")
                if not cursor.fetchone():
                    print("Error: patient_data table does not exist. It must be created first.")
                    return False
                
                # Create prediction_history table
                cursor.execute('''
                CREATE TABLE prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    prediction_score INTEGER,
                    prediction_date TIMESTAMP,
                    risk_level VARCHAR(20),
                    risk_factors TEXT,
                    recommendations TEXT,
                    feature_importances TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patient_data (id)
                )
                ''')
                sqlite_conn.commit()
                print("Table prediction_history created successfully")
            else:
                print("Table prediction_history exists, checking for feature_importances column")
                
                # Check if feature_importances column exists
                cursor.execute("PRAGMA table_info(prediction_history)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'feature_importances' not in column_names:
                    print("Adding feature_importances column to prediction_history table...")
                    cursor.execute("ALTER TABLE prediction_history ADD COLUMN feature_importances TEXT")
                    sqlite_conn.commit()
                    print("Column added successfully")
                else:
                    print("feature_importances column already exists")
            
            sqlite_conn.close()
        else:
            # PostgreSQL or other database approach
            metadata = MetaData()
            
            # Check if table exists
            inspector = inspect(engine)
            if 'prediction_history' not in inspector.get_table_names():
                print("Table prediction_history does not exist. Creating it...")
                
                # Create the table
                prediction_history = Table(
                    'prediction_history', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('patient_id', Integer, ForeignKey('patient_data.id'), nullable=False),
                    Column('prediction_score', Integer),
                    Column('prediction_date', DateTime, default=datetime.utcnow),
                    Column('risk_level', String(20)),
                    Column('risk_factors', Text),
                    Column('recommendations', Text),
                    Column('feature_importances', Text if 'postgresql' not in DATABASE_URI else JSONB)
                )
                
                metadata.create_all(engine)
                print("Table prediction_history created successfully")
            else:
                print("Table prediction_history exists, checking for feature_importances column")
                
                try:
                    # Check if the column exists
                    connection.execute(text("SELECT feature_importances FROM prediction_history LIMIT 1"))
                    print("feature_importances column already exists")
                except Exception as e:
                    if 'no such column' in str(e).lower() or 'does not exist' in str(e).lower():
                        print("Adding feature_importances column to prediction_history table...")
                        # Add the column
                        if 'postgresql' in DATABASE_URI:
                            connection.execute(text("ALTER TABLE prediction_history ADD COLUMN feature_importances JSONB"))
                        else:
                            connection.execute(text("ALTER TABLE prediction_history ADD COLUMN feature_importances TEXT"))
                        print("Column added successfully")
                    else:
                        raise
        
        print("Migrations completed successfully")
        return True
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1) 