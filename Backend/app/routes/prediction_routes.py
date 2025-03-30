from flask import Blueprint
from app.controllers.prediction_controller import PredictionController

# Create blueprint
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/prediction')

# Register routes
prediction_bp.route('/patient-data', methods=['POST'])(PredictionController.save_patient_data)
prediction_bp.route('/patient-data', methods=['GET'])(PredictionController.get_patient_data)
prediction_bp.route('/predict', methods=['POST'])(PredictionController.predict_hypertension)
prediction_bp.route('/history', methods=['GET'])(PredictionController.get_prediction_history)