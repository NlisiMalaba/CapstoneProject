from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.services.auth_service import AuthService

class AuthController:
    @staticmethod
    def register():
        """Register a new user."""
        data = request.get_json()
        
        # Validate input
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Process registration
        result, status_code = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'user')
        )
        
        return jsonify(result), status_code
    
    @staticmethod
    def login():
        """Authenticate a user and return JWT token."""
        data = request.get_json()
        
        # Validate input
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Process login
        result, status_code = AuthService.login_user(
            username=data['username'],
            password=data['password']
        )
        
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def refresh_token():
        """Refresh access token."""
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'access_token': new_access_token
        }), 200
    
    @staticmethod
    @jwt_required()
    def get_current_user():
        """Get current user info."""
        from app.models.user import User
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200