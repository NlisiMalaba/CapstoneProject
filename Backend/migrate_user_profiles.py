#!/usr/bin/env python
"""
Script to create the user_profiles table and update the patient_data table.
"""
from app.migrations.create_user_profiles_table import create_user_profiles_table
from app.migrations.update_patient_data_nullable import update_patient_data_table
from app.config import config
from app.database import init_db
from flask import Flask
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/migration.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the migrations."""
    logger.info("Starting migrations...")
    
    # Set up Flask app
    app = Flask(__name__)
    app.config.from_object(config['development'])
    init_db(app)
    
    # Run migrations
    success_profiles = create_user_profiles_table()
    success_patient_data = update_patient_data_table()
    
    if success_profiles and success_patient_data:
        logger.info("All migrations completed successfully")
    else:
        if not success_profiles:
            logger.error("User profiles migration failed")
        if not success_patient_data:
            logger.error("Patient data migration failed")
    
    return success_profiles and success_patient_data

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 