from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.prediction_service import PredictionService
from app.models.patient_data import PatientData
from app.models.prediction_history import PredictionHistory
from app.services.user_profile_service import user_profile_service
from app.database import db
from sqlalchemy.sql import text

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
        
        # Get user profile first to fill in missing fields
        profile_data = user_profile_service.get_profile(user_id)
        if profile_data:
            # Fill in important fields from profile if not provided in request
            if 'age' not in data or not data['age']:
                data['age'] = profile_data.age
            if 'gender' not in data or not data['gender']:
                data['gender'] = profile_data.gender
            if 'bmi' not in data or not data['bmi']:
                if profile_data.bmi:
                    data['bmi'] = profile_data.bmi
                elif profile_data.height and profile_data.weight:
                    height_in_meters = profile_data.height / 100
                    data['bmi'] = round(profile_data.weight / (height_in_meters * height_in_meters), 2)
        
        # Save patient data without requiring specific fields
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
        
        # Check if we have user profile data that can supplement the patient data
        profile_data = user_profile_service.get_profile(user_id)
        profile_message = ""
        
        if profile_data:
            profile_message = "Your profile data will be used to supplement missing patient data for predictions."
        
        # Convert to dictionary (excluding some fields)
        data = {c.name: getattr(patient_data, c.name) for c in patient_data.__table__.columns 
                if c.name not in ['id', 'user_id', 'created_at', 'updated_at']}
        
        return jsonify({
            'success': True,
            'patient_data': data,
            'profile_data_available': profile_data is not None,
            'profile_message': profile_message
        }), 200
    
    @staticmethod
    @jwt_required()
    def predict_hypertension():
        """Generate hypertension prediction for the current user."""
        user_id = get_jwt_identity()
        
        # First, check if user profile exists and has required data
        profile_data = user_profile_service.get_profile(user_id)
        missing_fields = []
        
        # Always verify profile data is available
        if not profile_data:
            missing_fields.append('profile data')
        else:
            if not profile_data.age:
                missing_fields.append('age')
            if not profile_data.gender:
                missing_fields.append('gender')
            if not profile_data.bmi and (not profile_data.height or not profile_data.weight):
                missing_fields.append('height and weight')
        
        # Return helpful error if profile data is missing required fields
        if missing_fields:
            return jsonify({
                'success': False, 
                'message': f'Missing required profile information: {", ".join(missing_fields)}',
                'missing_fields': missing_fields
            }), 400
            
        # Create a new patient data record for this prediction
        new_patient_data = PatientData(user_id=user_id)
        
        # Fill in data from profile
        if profile_data:
            if profile_data.age:
                new_patient_data.age = profile_data.age
            if profile_data.gender:
                new_patient_data.gender = profile_data.gender
            if profile_data.bmi:
                new_patient_data.bmi = profile_data.bmi
            elif profile_data.height and profile_data.weight:
                height_in_meters = profile_data.height / 100
                new_patient_data.bmi = round(profile_data.weight / (height_in_meters * height_in_meters), 2)
        
        # Save the new patient data record
        db.session.add(new_patient_data)
        db.session.commit()
        
        print(f"Created new patient data record with ID: {new_patient_data.id}")
            
        # Run prediction with the new patient data
        result, status_code = prediction_service.predict_hypertension(new_patient_data)
        
        if 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), status_code
        
        # Add a message about profile data usage
        if not result.get('is_mock', False):
            result['using_profile_data'] = True
            result['profile_message'] = "Your prediction includes data from your user profile."
        else:
            result['profile_message'] = "This is a demo prediction using your profile data."
        
        return jsonify({
            'success': True,
            'prediction': result
        }), status_code
    
    @staticmethod
    @jwt_required()
    def get_prediction_history():
        """Get prediction history for the current user."""
        try:
            user_id = get_jwt_identity()
            
            # Get all patient data records for this user
            patient_records = PatientData.query.filter_by(user_id=user_id).all()
            
            if not patient_records:
                return jsonify({
                    'success': True, 
                    'prediction_history': []
                }), 200
            
            # Get all predictions from prediction_history for all patient records
            try:
                all_predictions = []
                
                # Get patient IDs
                patient_ids = [p.id for p in patient_records]
                
                # Fetch all predictions for this user's patient records
                predictions = PredictionHistory.query\
                    .filter(PredictionHistory.patient_id.in_(patient_ids))\
                    .order_by(PredictionHistory.prediction_date.desc())\
                    .all()
                
                if not predictions:
                    return jsonify({
                        'success': True, 
                        'prediction_history': []
                    }), 200
                
                # Return all predictions
                prediction_data = [p.serialize for p in predictions]
                
                return jsonify({
                    'success': True,
                    'prediction_history': prediction_data
                }), 200
            except Exception as e:
                print(f"Database query error: {str(e)}")
                # If there's an error with the query (e.g., missing column), try a simplified query
                try:
                    # Use a more basic query with text() that works with SQLite and PostgreSQL
                    result = db.session.execute(
                        text("""
                        SELECT ph.id, ph.patient_id, ph.prediction_score, ph.prediction_date, 
                               ph.risk_level, ph.risk_factors, ph.recommendations
                        FROM prediction_history ph
                        JOIN patient_data pd ON ph.patient_id = pd.id
                        WHERE pd.user_id = :user_id
                        ORDER BY ph.prediction_date DESC
                        """),
                        {"user_id": user_id}
                    )
                    
                    # Manually process results
                    prediction_data = []
                    for row in result:
                        prediction_data.append({
                            'id': row[0],
                            'patient_id': row[1],
                            'prediction_score': row[2],
                            'prediction_date': row[3].isoformat() if row[3] else None,
                            'risk_level': row[4],
                            'risk_factors': row[5].split(',') if row[5] else [],
                            'recommendations': row[6].split(',') if row[6] else [],
                            'feature_importances': None  # Set to None since we can't get this
                        })
                    
                    return jsonify({
                        'success': True,
                        'prediction_history': prediction_data
                    }), 200
                except Exception as inner_e:
                    print(f"Fallback query error: {str(inner_e)}")
                    return jsonify({
                        'success': False,
                        'message': 'Error retrieving prediction history due to database schema issue.',
                        'error': str(inner_e)
                    }), 500
        except Exception as e:
            print(f"Prediction history error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve prediction history. Please try again later.',
                'error': str(e)
            }), 500