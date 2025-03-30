import os
from app.main import create_app
import argparse
from app.ml_model.train_model import main as train_model
import shutil

def setup_project():
    """Set up the project structure and sample data."""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Create model directory
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'ml_model')
    os.makedirs(model_dir, exist_ok=True)
    
    # Create static directory for Swagger
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Copy swagger.json to static directory if not present
    swagger_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'swagger.json')
    swagger_dest = os.path.join(static_dir, 'swagger.json')
    
    if not os.path.exists(swagger_dest) and os.path.exists(swagger_source):
        shutil.copy(swagger_source, swagger_dest)
    
    # Check if model already exists
    model_path = os.path.join(model_dir, 'model.pkl')
    if not os.path.exists(model_path):
        print("Training ML model...")
        train_model()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Hypertension Prediction API')
    parser.add_argument('--env', type=str, default='development', 
                        choices=['development', 'testing', 'production'],
                        help='Environment configuration')
    parser.add_argument('--port', type=int, default=5000, 
                        help='Port to run the application on')
    
    args = parser.parse_args()
    
    # Setup project structure
    setup_project()
    
    # Create app with specified environment
    app = create_app(args.env)
    
    # Run app
    app.run(host='0.0.0.0', port=args.port)