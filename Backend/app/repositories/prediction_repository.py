from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.models.prediction import Prediction
from app.models.medical_history import MedicalHistory

class PredictionRepository:
    def get_prediction(self, db: Session, prediction_id: int) -> Optional[Prediction]:
        """Get prediction by ID."""
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    def get_predictions_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Prediction]:
        """Get predictions for a user."""
        return db.query(Prediction)\
            .filter(Prediction.user_id == user_id)\
            .order_by(Prediction.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def create_prediction(
        self, 
        db: Session, 
        user_id: int, 
        medical_history_id: int, 
        prediction_data: Dict[str, Any]
    ) -> Prediction:
        """Create a new prediction."""
        # Convert feature_importances to JSON string
        if 'feature_importances' in prediction_data and isinstance(prediction_data['feature_importances'], dict):
            prediction_data['feature_importances'] = json.dumps(prediction_data['feature_importances'])
        
        db_prediction = Prediction(
            user_id=user_id,
            medical_history_id=medical_history_id,
            prediction_score=prediction_data.get('prediction_score'),
            prediction_probability=prediction_data.get('prediction_probability'),
            model_version=prediction_data.get('model_version', '1.0'),
            feature_importances=prediction_data.get('feature_importances'),
            recommendations=prediction_data.get('recommendations')
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    def get_latest_prediction_for_user(self, db: Session, user_id: int) -> Optional[Prediction]:
        """Get the latest prediction for a user."""
        return db.query(Prediction)\
            .filter(Prediction.user_id == user_id)\
            .order_by(Prediction.created_at.desc())\
            .first()
    
    def get_predictions_for_medical_history(self, db: Session, medical_history_id: int) -> List[Prediction]:
        """Get all predictions for a specific medical history."""
        return db.query(Prediction)\
            .filter(Prediction.medical_history_id == medical_history_id)\
            .order_by(Prediction.created_at.desc())\
            .all()