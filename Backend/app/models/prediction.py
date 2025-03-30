from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medical_history_id = Column(Integer, ForeignKey("medical_histories.id"), nullable=False)
    
    # Prediction score (0-100)
    prediction_score = Column(Float, nullable=False)
    
    # Raw prediction probability from model (0-1)
    prediction_probability = Column(Float, nullable=False)
    
    # Model used for prediction
    model_version = Column(String, nullable=False)
    
    # Feature importances for explainability
    feature_importances = Column(JSON)
    
    # Recommendations based on prediction
    recommendations = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="predictions")
    medical_history = relationship("MedicalHistory", backref="predictions")
    
    def __repr__(self):
        return f"<Prediction user_id={self.user_id}, score={self.prediction_score}>"