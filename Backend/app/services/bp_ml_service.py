import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.models.blood_pressure import BloodPressure
from flask import current_app
from app.database import db

class BPMLService:
    """Machine learning service for blood pressure analysis"""
    
    def detect_anomalies(self, user_id, days=90):
        """
        Detect anomalies in blood pressure readings using Isolation Forest
        Returns anomalous readings and their details
        """
        try:
            # Get user's BP readings from the past X days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            readings = BloodPressure.query.filter_by(user_id=user_id)\
                .filter(BloodPressure.measurement_date >= start_date)\
                .order_by(BloodPressure.measurement_date)\
                .all()
            
            if len(readings) < 10:
                return {
                    "success": False,
                    "message": "Insufficient data for anomaly detection. Need at least 10 readings."
                }, 400
            
            # Prepare data for analysis
            data = self._prepare_data_for_analysis(readings)
            
            # Detect anomalies
            anomalies = self._run_anomaly_detection(data)
            
            # Update anomaly status in database
            self._update_anomaly_status(anomalies, readings)
            
            # Format response with anomaly details
            return self._format_anomaly_response(anomalies, readings), 200
            
        except Exception as e:
            current_app.logger.error(f"Error in anomaly detection: {str(e)}")
            return {"success": False, "message": f"Error in anomaly detection: {str(e)}"}, 500
    
    def predict_bp_trend(self, user_id, days=30, prediction_days=7):
        """
        Predict blood pressure trend for the next X days
        Returns predicted values and confidence intervals
        """
        try:
            # Get user's BP readings
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            readings = BloodPressure.query.filter_by(user_id=user_id)\
                .filter(BloodPressure.measurement_date >= start_date)\
                .order_by(BloodPressure.measurement_date)\
                .all()
            
            if len(readings) < 7:
                return {
                    "success": False,
                    "message": "Insufficient data for trend prediction. Need at least 7 readings."
                }, 400
            
            # Prepare time series data
            data = self._prepare_data_for_analysis(readings)
            
            # Perform time series prediction (simplified here)
            predictions = self._predict_time_series(data, prediction_days)
            
            return {
                "success": True,
                "predictions": predictions
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error in BP trend prediction: {str(e)}")
            return {"success": False, "message": f"Error in BP trend prediction: {str(e)}"}, 500
    
    def analyze_factors(self, user_id):
        """
        Analyze which factors contribute to BP variations
        Returns significant factors and their correlation with BP
        """
        try:
            # This would analyze various factors like time of day, 
            # medication, activity, etc. to identify patterns
            
            # Placeholder implementation
            return {
                "success": True,
                "message": "Factor analysis not yet implemented",
                "factors": []
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error in factor analysis: {str(e)}")
            return {"success": False, "message": f"Error in factor analysis: {str(e)}"}, 500
    
    def _prepare_data_for_analysis(self, readings):
        """Prepare BP readings data for analysis"""
        # Extract features
        data = pd.DataFrame([{
            'date': r.measurement_date,
            'systolic': r.systolic,
            'diastolic': r.diastolic,
            'pulse': r.pulse if r.pulse else 0,
            'time_of_day': self._encode_time_of_day(r.measurement_time),
            'reading_id': r.id
        } for r in readings])
        
        # Add derived features
        data['pulse_pressure'] = data['systolic'] - data['diastolic']
        data['mean_arterial_pressure'] = data['diastolic'] + (data['pulse_pressure'] / 3)
        
        # Add time-based features
        data['hour'] = data['date'].apply(lambda x: x.hour)
        data['day_of_week'] = data['date'].apply(lambda x: x.weekday())
        
        return data
    
    def _encode_time_of_day(self, time_str):
        """Convert time string to numeric value"""
        if not time_str:
            return 0
            
        time_mapping = {
            'morning': 0,
            'afternoon': 1,
            'evening': 2,
            'night': 3
        }
        
        return time_mapping.get(time_str.lower(), 0)
    
    def _run_anomaly_detection(self, data):
        """Run Isolation Forest for anomaly detection"""
        # Select features for anomaly detection
        features = data[['systolic', 'diastolic', 'pulse_pressure', 'mean_arterial_pressure']]
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Initialize and fit Isolation Forest
        model = IsolationForest(
            n_estimators=100,
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42
        )
        
        # Fit model and predict anomalies (-1 for anomalies, 1 for normal)
        predictions = model.fit_predict(scaled_features)
        
        # Convert to boolean (True for anomalies)
        anomalies = predictions == -1
        
        # Add anomaly flag to data
        data['is_anomaly'] = anomalies
        
        # Calculate anomaly score
        data['anomaly_score'] = model.decision_function(scaled_features)
        
        # Return only anomalous readings
        return data[data['is_anomaly']]
    
    def _update_anomaly_status(self, anomalies, readings):
        """Update anomaly status in database"""
        if anomalies.empty:
            return
            
        # Map of reading IDs to update
        anomaly_ids = set(anomalies['reading_id'].values)
        
        for reading in readings:
            if reading.id in anomaly_ids:
                reading.is_abnormal = True
                reading.abnormality_details = "Detected as anomaly by machine learning model."
                
        db.session.commit()
    
    def _format_anomaly_response(self, anomalies, readings):
        """Format anomaly detection response"""
        if anomalies.empty:
            return {
                "success": True,
                "anomalies_found": False,
                "message": "No anomalies detected in the blood pressure readings."
            }
        
        # Format anomaly details
        anomaly_details = []
        for _, row in anomalies.iterrows():
            reading = next((r for r in readings if r.id == row['reading_id']), None)
            if reading:
                anomaly_details.append({
                    "reading_id": reading.id,
                    "date": reading.measurement_date.isoformat(),
                    "systolic": reading.systolic,
                    "diastolic": reading.diastolic,
                    "anomaly_score": float(row['anomaly_score']),
                    "category": reading.category
                })
        
        return {
            "success": True,
            "anomalies_found": True,
            "anomaly_count": len(anomaly_details),
            "anomalies": anomaly_details,
            "message": "Anomalies detected in blood pressure readings. Please review and consult healthcare provider if needed."
        }
    
    def _predict_time_series(self, data, prediction_days):
        """Simple time series prediction for BP trends"""
        # This is a placeholder implementation
        # A real implementation would use a proper time series model like ARIMA, Prophet, etc.
        
        # Calculate average trend over the period
        systolic_values = data['systolic'].values
        diastolic_values = data['diastolic'].values
        
        # Calculate simple linear trends
        days = np.arange(len(systolic_values))
        sys_coef = np.polyfit(days, systolic_values, 1)
        dia_coef = np.polyfit(days, diastolic_values, 1)
        
        # Generate predictions
        future_days = np.arange(len(systolic_values), len(systolic_values) + prediction_days)
        sys_pred = np.polyval(sys_coef, future_days)
        dia_pred = np.polyval(dia_coef, future_days)
        
        # Calculate confidence intervals (simplified)
        sys_std = np.std(systolic_values)
        dia_std = np.std(diastolic_values)
        
        # Format predictions
        predictions = []
        start_date = data['date'].max()
        for i in range(prediction_days):
            pred_date = start_date + timedelta(days=i+1)
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "systolic": {
                    "predicted": round(float(sys_pred[i]), 1),
                    "lower_bound": round(float(sys_pred[i] - 1.96 * sys_std), 1),
                    "upper_bound": round(float(sys_pred[i] + 1.96 * sys_std), 1)
                },
                "diastolic": {
                    "predicted": round(float(dia_pred[i]), 1),
                    "lower_bound": round(float(dia_pred[i] - 1.96 * dia_std), 1),
                    "upper_bound": round(float(dia_pred[i] + 1.96 * dia_std), 1)
                }
            })
        
        return predictions 