from app.database import db
from datetime import datetime

class UserProfile(db.Model):
    """User profile model for storing physical and demographic details."""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Physical and demographic details
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other
    weight = db.Column(db.Float, nullable=True)  # in kg
    height = db.Column(db.Float, nullable=True)  # in cm
    
    # BMI calculated field
    bmi = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('profile', uselist=False, lazy=True))
    
    def __repr__(self):
        return f'<UserProfile {self.id}, User {self.user_id}>'
    
    def calculate_bmi(self):
        """Calculate BMI if weight and height are available."""
        if self.weight and self.height and self.height > 0:
            # BMI = weight(kg) / (height(m))²
            height_in_meters = self.height / 100
            self.bmi = round(self.weight / (height_in_meters * height_in_meters), 2)
        return self.bmi 