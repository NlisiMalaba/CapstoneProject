from app.database import db
from app.models.user_profile import UserProfile
import logging

logger = logging.getLogger(__name__)

def create_user_profiles_table():
    """
    Migration script to create the user_profiles table.
    """
    try:
        # Create the table
        logger.info("Creating user_profiles table...")
        UserProfile.__table__.create(db.engine, checkfirst=True)
        logger.info("Successfully created user_profiles table")
        return True
    except Exception as e:
        logger.error(f"Error creating user_profiles table: {str(e)}")
        return False

if __name__ == "__main__":
    # For running directly
    import sys
    import os
    # Add parent directory to path for imports to work
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from app.config import config
    from app.database import init_db
    from flask import Flask
    
    app = Flask(__name__)
    app.config.from_object(config['development'])
    init_db(app)
    
    success = create_user_profiles_table()
    print(f"Migration {'successful' if success else 'failed'}")
    sys.exit(0 if success else 1) 