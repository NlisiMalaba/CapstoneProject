from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.bp_service import BPService
from datetime import datetime
import os

bp_service = BPService()

class BPController:
    @staticmethod
    @jwt_required()
    def add_bp_reading():
        """Add a new blood pressure reading."""
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Validate input
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['systolic', 'diastolic']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Process date if provided
        if 'measurement_date' in data and isinstance(data['measurement_date'], str):
            try:
                data['measurement_date'] = datetime.fromisoformat(data['measurement_date'])
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format'}), 400
        
        # Save BP reading
        result, status_code = bp_service.save_bp_reading(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), status_code
        
        return jsonify({
            'success': True, 
            'message': 'Blood pressure reading saved successfully',
            'reading_id': result.id,
            'is_abnormal': result.is_abnormal,
            'category': result.category
        }), status_code
    
    @staticmethod
    @jwt_required()
    def upload_csv():
        """Upload BP readings from CSV file."""
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
            
        file = request.files['file']
        
        # Check if file is valid
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'message': 'File must be a CSV'}), 400
        
        # Process CSV file
        result, status_code = bp_service.process_csv_upload(user_id, file)
        
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def upload_image():
        """Upload image with BP readings for OCR extraction."""
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
            
        file = request.files['file']
        
        # Check if file is valid
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
            
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({
                'success': False, 
                'message': f'File must be an image ({", ".join(allowed_extensions)})'
            }), 400
        
        # Process image file
        result, status_code = bp_service.process_image_upload(user_id, file)
        
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def get_readings():
        """Get BP readings for the current user."""
        user_id = get_jwt_identity()
        
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', default=100, type=int)
        
        # Convert date strings to datetime objects
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid start_date format'}), 400
                
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid end_date format'}), 400
        
        # Get readings
        result, status_code = bp_service.get_user_readings(user_id, start_date, end_date, limit)
        
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def get_analytics():
        """Get BP analytics for the current user."""
        user_id = get_jwt_identity()
        
        # Parse query parameters
        days = request.args.get('days', default=30, type=int)
        
        # Generate analytics
        result, status_code = bp_service.generate_analytics(user_id, days)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'success': False, 'message': result['error']}), status_code
        
        # Format response
        response_data = {
            'success': True,
            'analytics': result.serialize if hasattr(result, 'serialize') else result
        }
        
        return jsonify(response_data), status_code
    
    @staticmethod
    @jwt_required()
    def detect_anomalies():
        """Detect anomalies in BP readings using ML."""
        user_id = get_jwt_identity()
        
        result, status_code = bp_service.detect_anomalies(user_id)
        
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def generate_report():
        """Generate PDF or Excel report of BP data."""
        user_id = get_jwt_identity()
        
        # Parse query parameters
        report_type = request.args.get('type', default='pdf')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate report type
        if report_type not in ['pdf', 'excel']:
            return jsonify({
                'success': False, 
                'message': 'Invalid report type. Must be "pdf" or "excel"'
            }), 400
        
        # Convert date strings to datetime objects
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid start_date format'}), 400
                
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid end_date format'}), 400
        
        # Generate report
        result, status_code = bp_service.generate_reports(user_id, report_type, start_date, end_date)
        
        if status_code != 200:
            return jsonify(result), status_code
        
        # If successful, return the report path
        return jsonify(result), status_code
    
    @staticmethod
    @jwt_required()
    def download_report():
        """Download a generated report."""
        user_id = get_jwt_identity()
        
        # Get report path from query parameter
        report_path = request.args.get('path')
        
        if not report_path:
            return jsonify({'success': False, 'message': 'No report path provided'}), 400
        
        # Security check: ensure the path belongs to the user
        # This is a simple check; you might want to enhance it
        if str(user_id) not in report_path:
            return jsonify({'success': False, 'message': 'Unauthorized access to report'}), 403
        
        # Check if file exists
        if not os.path.exists(report_path):
            return jsonify({'success': False, 'message': 'Report not found'}), 404
        
        # Determine MIME type based on file extension
        if report_path.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif report_path.endswith('.xlsx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            mime_type = 'application/octet-stream'
        
        # Return the file
        return send_file(
            report_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(report_path)
        ) 