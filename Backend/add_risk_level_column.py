from app.database import db
from app.main import create_app
from app.models.patient_data import PatientData
from sqlalchemy import text
import sqlalchemy.exc

def add_risk_level_column():
    """Add risk_level column to patient_data table if it doesn't exist."""
    print("Starting migration script to add risk_level column...")
    
    # Create app with development environment
    app = create_app('development')
    
    with app.app_context():
        # Add all required columns that may be missing
        for column_info in [
            ('risk_level', 'STRING(20)'),
            ('risk_factors', 'TEXT'),
            ('recommendations', 'TEXT')
        ]:
            column_name, column_type = column_info
            
            # Check if the column exists by examining the table info
            try:
                # Use pragmas to get table info in SQLite
                table_info = db.session.execute(
                    text("PRAGMA table_info(patient_data)")
                ).fetchall()
                
                # Check if our column exists in the table
                column_exists = any(col[1] == column_name for col in table_info)
                
                if column_exists:
                    print(f"{column_name} column already exists in patient_data table")
                else:
                    print(f"{column_name} column does not exist, adding it now...")
                    # Add the column using raw SQL
                    db.session.execute(
                        text(f'ALTER TABLE patient_data ADD COLUMN {column_name} {column_type}')
                    )
                    db.session.commit()
                    print(f"Successfully added {column_name} column to patient_data table")
            
            except Exception as e:
                db.session.rollback()
                print(f"Error working with {column_name} column: {str(e)}")

if __name__ == '__main__':
    add_risk_level_column() 