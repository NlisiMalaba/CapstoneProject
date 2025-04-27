from app.database import db
from app.models.user_profile import UserProfile
from datetime import datetime

class UserProfileService:
    def __init__(self):
        pass
    
    def get_profile(self, user_id):
        """Get user profile by user ID."""
        return UserProfile.query.filter_by(user_id=user_id).first()
    
    def create_profile(self, user_id, data):
        """Create a new user profile."""
        try:
            # Check if profile already exists
            existing_profile = self.get_profile(user_id)
            if existing_profile:
                return {'error': 'Profile already exists for this user. Please update instead.'}, 400
            
            # Create new profile
            profile = UserProfile(user_id=user_id)
            
            # Set profile data
            self._update_profile_data(profile, data)
            
            # Save to database
            db.session.add(profile)
            db.session.commit()
            
            return profile, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    def update_profile(self, user_id, data):
        """Update an existing user profile."""
        try:
            # Get profile
            profile = self.get_profile(user_id)
            if not profile:
                return {'error': 'User profile not found. Please create a profile first.'}, 404
            
            # Update profile data
            self._update_profile_data(profile, data)
            
            # Save to database
            db.session.commit()
            
            return profile, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    def delete_profile(self, user_id):
        """Delete a user profile."""
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return {'error': 'User profile not found'}, 404
            
            db.session.delete(profile)
            db.session.commit()
            
            return {'message': 'Profile deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    def _update_profile_data(self, profile, data):
        """Update profile fields from data dictionary."""
        if 'age' in data:
            profile.age = data.get('age')
        
        if 'gender' in data:
            profile.gender = data.get('gender')
        
        if 'weight' in data:
            profile.weight = data.get('weight')
        
        if 'height' in data:
            profile.height = data.get('height')
            
        if 'contact_email' in data:
            profile.contact_email = data.get('contact_email')
            
        if 'emergency_contact' in data:
            profile.emergency_contact = data.get('emergency_contact')
        
        # Calculate BMI if weight and height are provided
        profile.calculate_bmi()
        
        profile.updated_at = datetime.utcnow()

# Create an instance to be imported by other modules
user_profile_service = UserProfileService() 