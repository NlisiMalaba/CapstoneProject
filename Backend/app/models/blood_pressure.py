from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class BloodPressure(db.Model):
    """Blood pressure measurement model."""
    __tablename__ = 'blood_pressure'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # BP measurements
    systolic = db.Column(db.Integer, nullable=False)
    diastolic = db.Column(db.Integer, nullable=False)
    pulse = db.Column(db.Integer, nullable=True)
    
    # Metadata
    measurement_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    measurement_time = db.Column(db.String(10), nullable=True)  # e.g., "Morning", "Evening"
    notes = db.Column(db.Text, nullable=True)
    
    # Data source tracking
    source = db.Column(db.String(20), nullable=False)  # "manual", "csv", "image"
    source_filename = db.Column(db.String(255), nullable=True)
    
    # Analysis results
    is_abnormal = db.Column(db.Boolean, default=False)
    abnormality_details = db.Column(db.Text, nullable=True)
    
    # Classification based on thresholds
    category = db.Column(db.String(30), nullable=True)  # Normal, Elevated, Hypertension Stage 1, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('blood_pressure_readings', lazy=True))
    
    def __repr__(self):
        return f'<BloodPressure {self.id}: {self.systolic}/{self.diastolic} ({self.measurement_date})>'
    
    @property
    def serialize(self):
        """Return data in serializable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'systolic': self.systolic,
            'diastolic': self.diastolic,
            'pulse': self.pulse,
            'measurement_date': self.measurement_date.isoformat() if self.measurement_date else None,
            'measurement_time': self.measurement_time,
            'notes': self.notes,
            'source': self.source,
            'is_abnormal': self.is_abnormal,
            'abnormality_details': self.abnormality_details,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 