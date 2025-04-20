"""
Migration to update patient_data table, making age, gender, and BMI fields nullable.
This allows these values to be pulled from the user profile instead of being required in patient_data.
"""
from app.database import db
import logging

logger = logging.getLogger(__name__)

def update_patient_data_table():
    """
    Alters the patient_data table to make age, gender, and BMI nullable.
    """
    try:
        # Connect to database
        conn = db.engine.connect()
        
        # Check if table exists
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patient_data'")
        if not result.fetchone():
            logger.warning("patient_data table doesn't exist, nothing to update")
            return True
        
        # Execute ALTER TABLE statements for SQLite
        # SQLite doesn't support direct ALTER COLUMN, so we need to:
        # 1. Create a new table with the updated schema
        # 2. Copy data from the old table
        # 3. Drop the old table
        # 4. Rename the new table
        
        # Create a temporary table with the updated schema
        conn.execute("""
        CREATE TABLE patient_data_temp (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            age INTEGER,
            gender VARCHAR(10),
            current_smoker BOOLEAN DEFAULT 0,
            cigs_per_day INTEGER DEFAULT 0,
            bp_meds BOOLEAN DEFAULT 0,
            diabetes BOOLEAN DEFAULT 0,
            total_chol FLOAT,
            sys_bp FLOAT,
            dia_bp FLOAT,
            bmi FLOAT,
            heart_rate INTEGER,
            glucose FLOAT,
            diet_description TEXT,
            medical_history TEXT,
            physical_activity_level VARCHAR(20),
            kidney_disease BOOLEAN DEFAULT 0,
            heart_disease BOOLEAN DEFAULT 0,
            family_history_htn BOOLEAN DEFAULT 0,
            alcohol_consumption VARCHAR(20),
            salt_intake VARCHAR(20),
            stress_level VARCHAR(20),
            sleep_hours FLOAT,
            created_at DATETIME,
            updated_at DATETIME,
            prediction_score FLOAT,
            prediction_date DATETIME,
            risk_level VARCHAR(20),
            risk_factors TEXT,
            recommendations TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Copy data from the old table
        conn.execute("""
        INSERT INTO patient_data_temp
        SELECT * FROM patient_data
        """)
        
        # Drop the old table
        conn.execute("DROP TABLE patient_data")
        
        # Rename the new table
        conn.execute("ALTER TABLE patient_data_temp RENAME TO patient_data")
        
        # Log success
        logger.info("Successfully updated patient_data table to make age, gender, and BMI nullable")
        
        return True
    except Exception as e:
        logger.error(f"Error updating patient_data table: {str(e)}")
        return False 