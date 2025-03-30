from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.prediction_service import PredictionService
from app.models.patient_data import PatientData

prediction_service = PredictionService()

class PredictionController:
    @staticmethod
    @jwt_required()
    def save_patient_data():
        """Save or update patient data."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate input
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['age', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Save patient data
        result, status_code = prediction_service.save_patient_data(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), status_code
        
        return jsonify({
            'success': True, 
            'message': 'Patient data saved successfully',
            'patient_data_id': result.id
        }), status_code
    
    @staticmethod
    @jwt_required()
    def get_patient_data():
        """Get patient data for the current user."""
        user_id = get_jwt_identity()
        
        patient_data = PatientData.query.filter_by(user_id=user_id).first()
        
        if not patient_data:
            return jsonify({
                'success': False, 
                'message': 'No patient data found for this user'
            }), 404
        
        # Convert to dictionary (excluding some fields)
        data = {c.name: getattr(patient_data, c.name) for c in patient_data.__table__.columns 
                if c.name not in ['id', 'user_id', 'created_at', 'updated_at']}
        
        # Format dates
        if data.get('prediction_date'):
            data['prediction_date'] = data['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'patient_data': data
        }), 200
    
    @staticmethod
    @jwt_required()
    def predict_hypertension():
        """Generate hypertension prediction for the current user."""
        user_id = get_jwt_identity()
        
        # Get patient data
        patient_data = PatientData.query.filter_by(user_id=user_id).first()
        
        if not patient_data:
            return jsonify({
                'success': False, 
                'message': 'No patient data found. Please add patient data first.'
            }), 404
        
        # Run prediction
        result, status_code = prediction_service.predict_hypertension(patient_data)
        
        if 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), status_code
        
        return jsonify({
            'success': True,
            'prediction': result
        }), status_code
    
    @staticmethod
    @jwt_required()
    def get_prediction_history():
        """Get prediction history for the current user."""
        user_id = get_jwt_identity()
        
        # Get patient data with prediction
        patient_data = PatientData.query.filter_by(user_id=user_id).first()
        
        if not patient_data or not patient_data.prediction_score:
            return jsonify({
                'success': False, 
                'message': 'No prediction history found for this user'
            }), 404
        
        prediction_data = {
            'prediction_score': patient_data.prediction_score,
            'prediction_date': patient_data.prediction_date.strftime('%Y-%m-%d %H:%M:%S') if patient_data.prediction_date else None,
            'risk_level': prediction_service._get_risk_level(patient_data.prediction_score),
            'key_factors': prediction_service._identify_key_factors(patient_data)
        }
        
        return jsonify({
            'success': True,
            'prediction_history': prediction_data
        }), 200