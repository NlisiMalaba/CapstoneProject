from app.database import db
from datetime import datetime

class MedicationLog(db.Model):
    """Log of medication adherence."""
    __tablename__ = 'medication_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    reminder_id = db.Column(db.Integer, db.ForeignKey('medication_reminders.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False)  # 'taken', 'missed', 'skipped'
    taken_at = db.Column(db.DateTime, nullable=True)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reminder = db.relationship('MedicationReminder', backref=db.backref('logs', lazy=True))
    
    def __repr__(self):
        return f'<MedicationLog {self.id}, Medication {self.medication_id}, Status {self.status}>' 