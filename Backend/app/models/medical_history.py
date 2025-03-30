from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base

class MedicalHistory(Base):
    __tablename__ = "medical_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic demographics
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # 'M' or 'F'
    
    # Lifestyle factors
    current_smoker = Column(Boolean, default=False)
    cigs_per_day = Column(Integer, default=0)
    physical_activity_level = Column(String)  # 'low', 'moderate', 'high'
    diet_description = Column(Text)  # Free text for NLP processing
    
    # Clinical measurements
    sys_bp = Column(Float)  # Systolic blood pressure
    dia_bp = Column(Float)  # Diastolic blood pressure
    total_cholesterol = Column(Float)
    bmi = Column(Float)
    heart_rate = Column(Float)
    glucose = Column(Float)
    
    # Medical conditions
    bp_meds = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    kidney_disease = Column(Boolean, default=False)
    heart_disease = Column(Boolean, default=False)
    
    # Additional medical history
    medical_history_text = Column(Text)  # Free text for NLP processing
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="medical_histories")
    
    def __repr__(self):
        return f"<MedicalHistory user_id={self.user_id}>"