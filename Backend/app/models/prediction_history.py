from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class PredictionHistory(db.Model):
    __tablename__ = 'prediction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_data.id'), nullable=False)
    prediction_score = db.Column(db.Integer)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    risk_level = db.Column(db.String(20))
    risk_factors = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Add feature importances for visualization
    feature_importances = db.Column(db.JSON, nullable=True)
    
    # Relationship
    patient = db.relationship('PatientData', backref=db.backref('prediction_history', lazy=True, order_by=prediction_date.desc())) 
    
    def __repr__(self):
        return f'<PredictionHistory id={self.id}, patient_id={self.patient_id}, score={self.prediction_score}>'
    
    @property
    def serialize(self):
        """Return data in serializable format"""
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'prediction_score': self.prediction_score,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'risk_level': self.risk_level,
            'risk_factors': self.risk_factors.split(',') if self.risk_factors else [],
            'recommendations': self.recommendations.split(',') if self.recommendations else []
        }
        
        # Safely add feature_importances if the column exists
        try:
            data['feature_importances'] = self.feature_importances
        except:
            data['feature_importances'] = None
            
        return data 