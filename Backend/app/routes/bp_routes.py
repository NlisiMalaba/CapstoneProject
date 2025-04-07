from flask import Blueprint
from app.controllers.bp_controller import BPController

# Create blueprint
bp_bp = Blueprint('bp', __name__, url_prefix='/api/bp')

# Register routes
bp_bp.route('/readings', methods=['POST'])(BPController.add_bp_reading)
bp_bp.route('/readings', methods=['GET'])(BPController.get_readings)
bp_bp.route('/upload/csv', methods=['POST'])(BPController.upload_csv)
bp_bp.route('/upload/image', methods=['POST'])(BPController.upload_image)
bp_bp.route('/analytics', methods=['GET'])(BPController.get_analytics)
bp_bp.route('/anomalies', methods=['GET'])(BPController.detect_anomalies)
bp_bp.route('/report', methods=['GET'])(BPController.generate_report)
bp_bp.route('/report/download', methods=['GET'])(BPController.download_report) 