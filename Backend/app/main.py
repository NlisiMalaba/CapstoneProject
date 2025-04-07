from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import os

from app.config import config
from app.database import init_db
from app.routes.auth_routes import auth_bp
from app.routes.prediction_routes import prediction_bp
from app.routes.medication_routes import medication_bp
from app.routes.bp_routes import bp_bp

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(medication_bp)
    app.register_blueprint(bp_bp)
    
    # Register Swagger UI blueprint
    swagger_ui_blueprint = get_swaggerui_blueprint(
        app.config['SWAGGER_URL'],
        app.config['API_URL'],
        config={
            'app_name': "Hypertension Prediction API"
        }
    )
    app.register_blueprint(swagger_ui_blueprint)
    
    # Create static folder for Swagger JSON
    os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to the Hypertension Prediction API',
            'documentation': app.config['SWAGGER_URL']
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401
    
    return app