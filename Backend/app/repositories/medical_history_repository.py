from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.models.medical_history import MedicalHistory

class MedicalHistoryRepository:
    def get_medical_history(self, db: Session, medical_history_id: int) -> Optional[MedicalHistory]:
        """Get medical history by ID."""
        return db.query(MedicalHistory).filter(MedicalHistory.id == medical_history_id).first()
    
    def get_medical_histories_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[MedicalHistory]:
        """Get medical history entries for a user."""
        return db.query(MedicalHistory)\
            .filter(MedicalHistory.user_id == user_id)\
            .order_by(MedicalHistory.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def create_medical_history(self, db: Session, user_id: int, medical_data: Dict[str, Any]) -> MedicalHistory:
        """Create a new medical history entry."""
        db_medical_history = MedicalHistory(
            user_id=user_id,
            age=medical_data.get('age'),
            gender=medical_data.get('gender'),
            current_smoker=medical_data.get('current_smoker', False),
            cigs_per_day=medical_data.get('cigs_per_day', 0),
            physical_activity_level=medical_data.get('physical_activity_level'),
            diet_description=medical_data.get('diet_description', ''),
            sys_bp=medical_data.get('sys_bp'),
            dia_bp=medical_data.get('dia_bp'),
            total_cholesterol=medical_data.get('total_cholesterol'),
            bmi=medical_data.get('bmi'),
            heart_rate=medical_data.get('heart_rate'),
            glucose=medical_data.get('glucose'),
            bp_meds=medical_data.get('bp_meds', False),
            diabetes=medical_data.get('diabetes', False),
            kidney_disease=medical_data.get('kidney_disease', False),
            heart_disease=medical_data.get('heart_disease', False),
            medical_history_text=medical_data.get('medical_history_text', '')
        )
        
        db.add(db_medical_history)
        db.commit()
        db.refresh(db_medical_history)
        return db_medical_history
    
    def update_medical_history(self, db: Session, medical_history_id: int, medical_data: Dict[str, Any]) -> Optional[MedicalHistory]:
        """Update a medical history entry."""
        db_medical_history = self.get_medical_history(db, medical_history_id)
        
        if db_medical_history:
            for key, value in medical_data.items():
                if hasattr(db_medical_history, key):
                    setattr(db_medical_history, key, value)
            
            db.commit()
            db.refresh(db_medical_history)
            
        return db_medical_history
    
    def delete_medical_history(self, db: Session, medical_history_id: int) -> bool:
        """Delete a medical history entry."""
        db_medical_history = self.get_medical_history(db, medical_history_id)
        
        if db_medical_history:
            db.delete(db_medical_history)
            db.commit()
            return True
            
        return False
    
    def get_latest_medical_history_for_user(self, db: Session, user_id: int) -> Optional[MedicalHistory]:
        """Get the latest medical history for a user."""
        return db.query(MedicalHistory)\
            .filter(MedicalHistory.user_id == user_id)\
            .order_by(MedicalHistory.created_at.desc())\
            .first()