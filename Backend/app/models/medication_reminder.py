from app.database import db
from datetime import datetime
import secrets

class MedicationReminder(db.Model):
    """Medication reminder model for hypertension patients."""
    __tablename__ = 'medication_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    reminder_time = db.Column(db.DateTime, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_verification_code(self):
        """Generate a random 6-digit verification code."""
        self.verification_code = secrets.randbelow(1000000).__str__().zfill(6)
        return self.verification_code
    
    def __repr__(self):
        return f'<MedicationReminder {self.id}, Medication {self.medication_id}>' 