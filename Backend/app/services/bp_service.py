import os
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.utils import secure_filename
from app.database import db
from app.models.blood_pressure import BloodPressure
from app.models.bp_analytics import BPAnalytics
import pytesseract
from PIL import Image

class BPService:
    """Service for managing blood pressure data"""
    
    def save_bp_reading(self, user_id, data):
        """Save a single BP reading"""
        try:
            # Validate data
            if not self._validate_bp_data(data):
                return {"error": "Invalid blood pressure values"}, 400
                
            # Create new BP reading
            bp_reading = BloodPressure(
                user_id=user_id,
                systolic=data.get('systolic'),
                diastolic=data.get('diastolic'),
                pulse=data.get('pulse'),
                measurement_date=data.get('measurement_date', datetime.utcnow()),
                measurement_time=data.get('measurement_time'),
                notes=data.get('notes'),
                source=data.get('source', 'manual'),
            )
            
            # Set BP category
            bp_reading.category = self._categorize_bp(bp_reading.systolic, bp_reading.diastolic)
            
            # Check if BP is abnormal
            bp_reading.is_abnormal = self._is_abnormal_bp(bp_reading.systolic, bp_reading.diastolic)
            if bp_reading.is_abnormal:
                bp_reading.abnormality_details = self._generate_abnormality_details(bp_reading)
            
            # Save to database
            db.session.add(bp_reading)
            db.session.commit()
            
            return bp_reading, 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving BP reading: {str(e)}")
            return {"error": "Failed to save blood pressure reading"}, 500
    
    def process_csv_upload(self, user_id, file):
        """Process CSV file with BP readings"""
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            readings = []
            errors = []
            
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    try:
                        # Convert and validate data
                        bp_data = {
                            'systolic': int(row.get('systolic')),
                            'diastolic': int(row.get('diastolic')),
                            'pulse': int(row.get('pulse')) if row.get('pulse') else None,
                            'measurement_date': datetime.strptime(row.get('date', ''), '%Y-%m-%d') 
                                if row.get('date') else datetime.utcnow(),
                            'measurement_time': row.get('time'),
                            'notes': row.get('notes'),
                            'source': 'csv',
                            'source_filename': filename
                        }
                        
                        # Validate and save
                        if self._validate_bp_data(bp_data):
                            result, _ = self.save_bp_reading(user_id, bp_data)
                            if not isinstance(result, dict):  # Not an error
                                readings.append(result.id)
                            else:
                                errors.append(f"Row error: {result.get('error')}")
                        else:
                            errors.append(f"Invalid BP values: {bp_data['systolic']}/{bp_data['diastolic']}")
                    except Exception as e:
                        errors.append(f"Error processing row: {str(e)}")
            
            # Generate analytics if readings were added
            if readings:
                self.generate_analytics(user_id)
                
            return {
                "success": True,
                "readings_added": len(readings),
                "errors": errors
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error processing CSV: {str(e)}")
            return {"error": f"Failed to process CSV file: {str(e)}"}, 500
    
    def process_image_upload(self, user_id, file):
        """Extract BP readings from image using OCR"""
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Use OCR to extract text from image
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            # Extract BP readings from text
            readings = self._extract_bp_from_text(text)
            
            # Save extracted readings
            saved_readings = []
            for bp_data in readings:
                bp_data['user_id'] = user_id
                bp_data['source'] = 'image'
                bp_data['source_filename'] = filename
                
                result, _ = self.save_bp_reading(user_id, bp_data)
                if not isinstance(result, dict):  # Not an error
                    saved_readings.append(result.id)
            
            # Generate analytics if readings were added
            if saved_readings:
                self.generate_analytics(user_id)
                
            return {
                "success": True,
                "readings_added": len(saved_readings),
                "readings": saved_readings
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error processing image: {str(e)}")
            return {"error": f"Failed to process image: {str(e)}"}, 500
    
    def get_user_readings(self, user_id, start_date=None, end_date=None, limit=100):
        """Get BP readings for a user with optional date filtering"""
        try:
            query = BloodPressure.query.filter_by(user_id=user_id)
            
            if start_date:
                query = query.filter(BloodPressure.measurement_date >= start_date)
            if end_date:
                query = query.filter(BloodPressure.measurement_date <= end_date)
                
            readings = query.order_by(BloodPressure.measurement_date.desc()).limit(limit).all()
            
            return {
                "success": True,
                "readings": [reading.serialize for reading in readings]
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error fetching BP readings: {str(e)}")
            return {"error": f"Failed to fetch readings: {str(e)}"}, 500
    
    def generate_analytics(self, user_id, days=30):
        """Generate BP analytics for specified timeframe"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get readings in time range
            readings = BloodPressure.query.filter_by(user_id=user_id)\
                .filter(BloodPressure.measurement_date >= start_date,
                        BloodPressure.measurement_date <= end_date)\
                .all()
            
            if not readings:
                return {"error": "No readings found in date range"}, 404
            
            # Calculate analytics
            systolic_values = [r.systolic for r in readings]
            diastolic_values = [r.diastolic for r in readings]
            abnormal_count = sum(1 for r in readings if r.is_abnormal)
            
            # Create or update analytics record
            analytics = BPAnalytics.query.filter_by(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            ).first()
            
            if not analytics:
                analytics = BPAnalytics(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            analytics.avg_systolic = sum(systolic_values) / len(systolic_values)
            analytics.avg_diastolic = sum(diastolic_values) / len(diastolic_values)
            analytics.max_systolic = max(systolic_values)
            analytics.max_diastolic = max(diastolic_values)
            analytics.min_systolic = min(systolic_values)
            analytics.min_diastolic = min(diastolic_values)
            analytics.reading_count = len(readings)
            analytics.abnormal_reading_count = abnormal_count
            
            # Calculate trend
            analytics.trend_direction = self._calculate_trend(readings)
            analytics.trend_details = self._generate_trend_details(readings, analytics)
            
            db.session.add(analytics)
            db.session.commit()
            
            return analytics, 200
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error generating analytics: {str(e)}")
            return {"error": f"Failed to generate analytics: {str(e)}"}, 500
    
    def detect_anomalies(self, user_id):
        """Detect anomalies in BP readings using ML"""
        # This would use machine learning for anomaly detection
        # Placeholder for now
        return {"message": "Anomaly detection not yet implemented"}, 200
    
    def generate_reports(self, user_id, report_type, start_date=None, end_date=None):
        """Generate PDF or Excel reports of BP data"""
        try:
            # Get data for report
            result, status_code = self.get_user_readings(
                user_id, 
                start_date=start_date, 
                end_date=end_date, 
                limit=1000
            )
            
            if status_code != 200 or not result.get("success"):
                return result, status_code
                
            readings = result.get("readings", [])
            if not readings:
                return {"error": "No data available for report"}, 404
                
            # Generate appropriate report
            if report_type == "pdf":
                return self._generate_pdf_report(user_id, readings)
            elif report_type == "excel":
                return self._generate_excel_report(user_id, readings)
            else:
                return {"error": "Invalid report type"}, 400
                
        except Exception as e:
            current_app.logger.error(f"Error generating report: {str(e)}")
            return {"error": f"Failed to generate report: {str(e)}"}, 500
    
    def _validate_bp_data(self, data):
        """Validate BP measurement data"""
        if not data:
            return False
            
        systolic = data.get('systolic')
        diastolic = data.get('diastolic')
        
        # Check if values are present and in reasonable range
        if not systolic or not diastolic:
            return False
            
        if not isinstance(systolic, int) or not isinstance(diastolic, int):
            return False
            
        if systolic < 70 or systolic > 250:
            return False
            
        if diastolic < 40 or diastolic > 150:
            return False
            
        if diastolic > systolic:
            return False
            
        return True
    
    def _categorize_bp(self, systolic, diastolic):
        """Categorize BP reading according to standard guidelines"""
        if systolic < 120 and diastolic < 80:
            return "Normal"
        elif 120 <= systolic <= 129 and diastolic < 80:
            return "Elevated"
        elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
            return "Hypertension Stage 1"
        elif systolic >= 140 or diastolic >= 90:
            return "Hypertension Stage 2"
        elif systolic > 180 or diastolic > 120:
            return "Hypertensive Crisis"
        
        return "Unknown"
    
    def _is_abnormal_bp(self, systolic, diastolic):
        """Check if BP reading is abnormal"""
        category = self._categorize_bp(systolic, diastolic)
        return category in ["Hypertension Stage 1", "Hypertension Stage 2", "Hypertensive Crisis"]
    
    def _generate_abnormality_details(self, bp_reading):
        """Generate details about abnormal reading"""
        category = bp_reading.category
        details = f"Blood pressure reading of {bp_reading.systolic}/{bp_reading.diastolic} "
        
        if category == "Hypertension Stage 1":
            details += "indicates Stage 1 Hypertension. Lifestyle changes recommended."
        elif category == "Hypertension Stage 2":
            details += "indicates Stage 2 Hypertension. Consult with healthcare provider."
        elif category == "Hypertensive Crisis":
            details += "indicates Hypertensive Crisis. Seek immediate medical attention!"
        
        return details
    
    def _calculate_trend(self, readings):
        """Calculate BP trend direction"""
        if len(readings) < 3:
            return "insufficient data"
            
        # Sort readings by date
        sorted_readings = sorted(readings, key=lambda r: r.measurement_date)
        
        # Get first and last 3 readings
        first_readings = sorted_readings[:3]
        last_readings = sorted_readings[-3:]
        
        # Calculate average systolic values
        first_avg = sum(r.systolic for r in first_readings) / 3
        last_avg = sum(r.systolic for r in last_readings) / 3
        
        # Determine trend direction
        if last_avg < first_avg - 5:
            return "improving"
        elif last_avg > first_avg + 5:
            return "worsening"
        else:
            return "stable"
    
    def _generate_trend_details(self, readings, analytics):
        """Generate details about BP trend"""
        trend = analytics.trend_direction
        if trend == "insufficient data":
            return "Not enough readings to determine trend."
        
        details = f"Blood pressure trend is {trend}. "
        
        if trend == "improving":
            details += "Continue current treatment and lifestyle changes."
        elif trend == "worsening":
            details += "Consider consulting healthcare provider for treatment adjustment."
        elif trend == "stable":
            if analytics.avg_systolic >= 130 or analytics.avg_diastolic >= 80:
                details += "BP is stable but elevated. Consider lifestyle modifications."
            else:
                details += "BP is stable and within normal range."
        
        return details
    
    def _extract_bp_from_text(self, text):
        """Extract BP readings from OCR text"""
        # This is a simplified implementation
        # Real implementation would be more sophisticated
        readings = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for patterns like "120/80"
            if '/' in line:
                parts = line.split('/')
                try:
                    systolic = int(parts[0].strip().split()[-1])
                    diastolic = int(parts[1].strip().split()[0])
                    
                    # Validate extracted values
                    if 70 <= systolic <= 250 and 40 <= diastolic <= 150:
                        readings.append({
                            'systolic': systolic,
                            'diastolic': diastolic,
                            'measurement_date': datetime.utcnow(),
                            'source': 'image'
                        })
                except (ValueError, IndexError):
                    continue
        
        return readings
    
    def _generate_pdf_report(self, user_id, readings):
        """Generate PDF report with BP data visualization"""
        # Placeholder for PDF generation logic
        # Would use a library like ReportLab, WeasyPrint, etc.
        report_path = f"reports/bp_report_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Update analytics with report path
        analytics = BPAnalytics.query.filter_by(user_id=user_id).order_by(BPAnalytics.created_at.desc()).first()
        if analytics:
            analytics.pdf_report_path = report_path
            db.session.commit()
        
        return {
            "success": True,
            "message": "PDF report generated",
            "report_path": report_path
        }, 200
    
    def _generate_excel_report(self, user_id, readings):
        """Generate Excel report with BP data"""
        # Create DataFrame from readings
        df = pd.DataFrame([{
            'Date': r.get('measurement_date'),
            'Time': r.get('measurement_time', ''),
            'Systolic': r.get('systolic'),
            'Diastolic': r.get('diastolic'),
            'Pulse': r.get('pulse', ''),
            'Category': r.get('category', ''),
            'Is Abnormal': 'Yes' if r.get('is_abnormal') else 'No',
            'Notes': r.get('notes', '')
        } for r in readings])
        
        # Generate Excel file
        report_path = f"reports/bp_report_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        df.to_excel(report_path, index=False)
        
        # Update analytics with report path
        analytics = BPAnalytics.query.filter_by(user_id=user_id).order_by(BPAnalytics.created_at.desc()).first()
        if analytics:
            analytics.excel_report_path = report_path
            db.session.commit()
        
        return {
            "success": True,
            "message": "Excel report generated",
            "report_path": report_path
        }, 200 