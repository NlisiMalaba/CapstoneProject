from flask import Blueprint
from app.controllers.user_profile_controller import UserProfileController

# Create a blueprint for user profile routes
user_profile_bp = Blueprint('user_profile', __name__, url_prefix='/api/user-profile')

# Define routes
user_profile_bp.route('', methods=['GET'])(UserProfileController.get_profile)
user_profile_bp.route('', methods=['POST'])(UserProfileController.create_profile)
user_profile_bp.route('', methods=['PUT'])(UserProfileController.update_profile)
user_profile_bp.route('', methods=['DELETE'])(UserProfileController.delete_profile) 