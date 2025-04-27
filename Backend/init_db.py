"""
Initialize the database by creating all tables from models
"""
import os
from app.main import create_app
from app.database import db
import time

# Import all models so they are registered with SQLAlchemy
from app.models.user import User
from app.models.patient_data import PatientData
from app.models.prediction_history import PredictionHistory
from app.models.blood_pressure import BloodPressure
from app.models.user_profile import UserProfile

def init_db():
    # Create the Flask app with development config
    app = create_app('development')
    
    # Print environment info for debugging
    print(f"Current directory: {os.getcwd()}")
    
    # Check model path
    from app.services.ml_service import hypertension_prediction_service
    print(f"Model path: {hypertension_prediction_service.model_path}")
    if os.path.exists(hypertension_prediction_service.model_path):
        print(f"Model file exists with size: {os.path.getsize(hypertension_prediction_service.model_path)} bytes")
    else:
        print(f"Model file does not exist at path: {hypertension_prediction_service.model_path}")
        # Check common locations
        possible_paths = [
            os.path.join(os.getcwd(), 'app', 'ml_model', 'model.pkl'),
            os.path.join(os.getcwd(), 'ml_model', 'model.pkl'),
            os.path.join(os.getcwd(), 'Backend', 'app', 'ml_model', 'model.pkl')
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found model at alternative path: {path}")
                print(f"Consider updating MODEL_PATH config to point to this location")
    
    # Use app context to create database tables
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        time.sleep(1)  # Wait for tables to be created
        print("Database tables created successfully!")
        
        # Print the list of tables created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\nTables in the database:")
        for table in tables:
            print(f"- {table}")
            # Print columns for each table
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")

    print("\nDatabase initialization complete.")
    
if __name__ == "__main__":
    init_db() 