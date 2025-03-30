from app.database import db
from datetime import datetime

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_data.id'), nullable=False)
    prediction_score = db.Column(db.Integer)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    risk_level = db.Column(db.String(20))
    risk_factors = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Relationship
    patient = db.relationship('PatientData', backref=db.backref('prediction_history', lazy=True)) 