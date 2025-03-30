from app.database import db
from datetime import datetime

class PatientData(db.Model):
    """Patient data model for hypertension prediction."""
    __tablename__ = 'patient_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic demographic info
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female, Other
    
    # Framingham dataset variables
    current_smoker = db.Column(db.Boolean, default=False)
    cigs_per_day = db.Column(db.Integer, default=0)
    bp_meds = db.Column(db.Boolean, default=False)
    diabetes = db.Column(db.Boolean, default=False)
    total_chol = db.Column(db.Float, nullable=True)
    sys_bp = db.Column(db.Float, nullable=True)
    dia_bp = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    heart_rate = db.Column(db.Integer, nullable=True)
    glucose = db.Column(db.Float, nullable=True)
    
    # Additional fields
    diet_description = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    physical_activity_level = db.Column(db.String(20), nullable=True)  # Low, Moderate, High
    kidney_disease = db.Column(db.Boolean, default=False)
    heart_disease = db.Column(db.Boolean, default=False)
    family_history_htn = db.Column(db.Boolean, default=False)
    alcohol_consumption = db.Column(db.String(20), nullable=True)  # None, Light, Moderate, Heavy
    salt_intake = db.Column(db.String(20), nullable=True)  # Low, Moderate, High
    stress_level = db.Column(db.String(20), nullable=True)  # Low, Moderate, High
    sleep_hours = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prediction results
    prediction_score = db.Column(db.Float, nullable=True)
    prediction_date = db.Column(db.DateTime, nullable=True)
    
    # Risk level
    risk_level = db.Column(db.String(20))  # Low, Moderate, High, Very High
    
    # Risk factors
    risk_factors = db.Column(db.Text)  # Storing as comma-separated string
    
    # Recommendations
    recommendations = db.Column(db.Text)  # Storing as comma-separated string
    
    # Relationships
    user = db.relationship('User', backref=db.backref('patient_data', lazy=True))
    
    def __repr__(self):
        return f'<PatientData {self.id}, User {self.user_id}>'