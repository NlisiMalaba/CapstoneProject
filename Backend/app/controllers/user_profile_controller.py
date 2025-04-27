from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_profile_service import user_profile_service

class UserProfileController:
    @staticmethod
    @jwt_required()
    def get_profile():
        """Get user profile for the current user."""
        user_id = get_jwt_identity()
        
        profile = user_profile_service.get_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False, 
                'message': 'No profile found for this user'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': {
                'age': profile.age,
                'gender': profile.gender,
                'weight': profile.weight,
                'height': profile.height,
                'bmi': profile.bmi,
                'contact_email': profile.contact_email,
                'emergency_contact': profile.emergency_contact,
                'created_at': profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
    
    @staticmethod
    @jwt_required()
    def create_profile():
        """Create a user profile for the current user."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        result, status_code = user_profile_service.create_profile(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), status_code
        
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile': {
                'age': result.age,
                'gender': result.gender,
                'weight': result.weight,
                'height': result.height,
                'bmi': result.bmi,
                'contact_email': result.contact_email,
                'emergency_contact': result.emergency_contact
            }
        }), status_code
    
    @staticmethod
    @jwt_required()
    def update_profile():
        """Update the profile for the current user."""
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        result, status_code = user_profile_service.update_profile(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), status_code
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': {
                'age': result.age,
                'gender': result.gender,
                'weight': result.weight,
                'height': result.height,
                'bmi': result.bmi,
                'contact_email': result.contact_email,
                'emergency_contact': result.emergency_contact
            }
        }), status_code
    
    @staticmethod
    @jwt_required()
    def delete_profile():
        """Delete the profile for the current user."""
        user_id = get_jwt_identity()
        
        result, status_code = user_profile_service.delete_profile(user_id)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), status_code
        
        return jsonify({
            'success': True,
            'message': result['message']
        }), status_code 