from app.database import db
from datetime import datetime

class Medication(db.Model):
    """Medication model for hypertension patients."""
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # e.g., "once daily", "twice daily"
    time_of_day = db.Column(db.String(100), nullable=False)  # JSON string of times
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('medications', lazy=True))
    reminders = db.relationship('MedicationReminder', backref='medication', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('MedicationLog', backref='medication', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medication {self.name}, User {self.user_id}>' 