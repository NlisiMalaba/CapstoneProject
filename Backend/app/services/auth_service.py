from app.models.user import User
from app.database import db
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime

class AuthService:
    @staticmethod
    def register_user(username, email, password, role='user'):
        """Register a new user."""
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': 'Username already exists'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Email already exists'}, 400
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.password = password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return {'success': True, 'message': 'User registered successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Error: {str(e)}'}, 500
    
    @staticmethod
    def login_user(username, password):
        """Authenticate a user and return JWT tokens."""
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.verify_password(password):
            return {'success': False, 'message': 'Invalid username or password'}, 401
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }, 200