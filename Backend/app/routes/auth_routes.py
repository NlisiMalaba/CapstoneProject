from flask import Blueprint
from app.controllers.auth_controller import AuthController

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Register routes
auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/refresh', methods=['POST'])(AuthController.refresh_token)
auth_bp.route('/me', methods=['GET'])(AuthController.get_current_user)