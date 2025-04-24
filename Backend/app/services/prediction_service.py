import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.models.patient_data import PatientData
from app.models.blood_pressure import BloodPressure
from app.database import db
from app.utils.text_processor import extract_features_from_text
from app.models.prediction_history import PredictionHistory
from app.services.ml_service import hypertension_prediction_service
from app.services.user_profile_service import user_profile_service

class PredictionService:
    def __init__(self):
        # Load the model and vectorizer
        self.model = hypertension_prediction_service.model
        self.vectorizer = hypertension_prediction_service.vectorizer
    
    def save_patient_data(self, user_id, data):
        """Save or update patient data for a user."""
        try:
            # Check if patient data exists
            patient_data = PatientData.query.filter_by(user_id=user_id).first()
            
            if patient_data:
                # Update existing data
                for key, value in data.items():
                    # Don't update BP values as we'll get them from BP readings
                    if key not in ['sys_bp', 'dia_bp', 'heart_rate']:
                        setattr(patient_data, key, value)
                patient_data.updated_at = datetime.utcnow()
            else:
                # Create new patient data - filter out BP values
                bp_fields = ['sys_bp', 'dia_bp', 'heart_rate']
                filtered_data = {k: v for k, v in data.items() if k not in bp_fields}
                filtered_data['user_id'] = user_id
                patient_data = PatientData(**filtered_data)
                db.session.add(patient_data)
            
            db.session.commit()
            return patient_data, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    def predict_hypertension(self, patient_data):
        """Generate hypertension prediction for patient data."""
        try:
            # Make sure model is loaded
            if self.model is None:
                # Use mock prediction since model isn't available
                print("Model not loaded - using mock prediction data for testing")
                return self._generate_mock_prediction(patient_data), 200
            
            # Get user profile data to use instead of asking user repeatedly
            user_profile = user_profile_service.get_profile(patient_data.user_id)
            
            # If user profile exists, update patient data with profile values
            profile_updated = False
            if user_profile:
                profile_updated = self._update_patient_data_from_profile(patient_data, user_profile)
            
            # Check if required profile-based data is available
            missing_data = []
            if patient_data.age is None or patient_data.age == 0:
                missing_data.append("age")
            if not patient_data.gender:
                missing_data.append("gender")
            if patient_data.bmi is None or patient_data.bmi == 0:
                missing_data.append("BMI (or height and weight)")
            
            # If critical data is missing, return error
            if missing_data:
                return {
                    'error': f"Missing required data: {', '.join(missing_data)}. Please complete your user profile.",
                    'missing_fields': missing_data
                }, 400
            
            # Get blood pressure data from blood_pressure table
            bp_data = self._get_blood_pressure_averages(patient_data.user_id)
            if bp_data:
                # Update blood pressure values from BP readings
                patient_data.sys_bp = bp_data['avg_systolic']
                patient_data.dia_bp = bp_data['avg_diastolic']
                patient_data.heart_rate = bp_data['avg_pulse']
                # Save these updates
                db.session.commit()
            
            # Extract structured features
            structured_features = self._extract_structured_features(patient_data)
            print(f"Structured features shape: {structured_features.shape}")
            
            # Since the model expects 27 features and we have 20 structured features,
            # we'll allocate 7 features for text (27 - 20 = 7)
            expected_text_features = 7
            
            # Extract text features if available
            text_features = self._extract_text_features(patient_data, expected_features=expected_text_features)
            if text_features is not None:
                print(f"Text features shape: {text_features.shape}")
            
            # Combine features
            all_features = np.hstack([structured_features, text_features]) if text_features is not None else structured_features
            
            print(f"Total features: {all_features.shape[0]}, Expected: {self.model.n_features_in_}")
            
            # Make prediction
            prediction_prob = self.model.predict_proba(all_features.reshape(1, -1))[0][1]
            prediction_score = int(round(prediction_prob * 100))
            
            # Apply medical knowledge rules to adjust the score if needed
            adjusted_score = self._apply_medical_rules(patient_data, prediction_score)
            if adjusted_score != prediction_score:
                print(f"Score adjusted from {prediction_score}% to {adjusted_score}% based on medical rules")
            
            risk_level = self._get_risk_level(adjusted_score)
            
            # Identify risk factors
            key_factors = self._identify_key_factors(patient_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(patient_data, key_factors)
            
            # Extract feature importances for visualization
            feature_importances = self._extract_feature_importances()
            
            # Save prediction results to prediction_history table
            try:
                # Create new prediction history record
                prediction_history = PredictionHistory(
                    patient_id=patient_data.id,
                    prediction_score=adjusted_score,
                    prediction_date=datetime.utcnow(),
                    risk_level=risk_level,
                    risk_factors=','.join(key_factors) if key_factors else '',
                    recommendations=','.join(recommendations) if recommendations else '',
                    feature_importances=feature_importances
                )
                
                db.session.add(prediction_history)
                db.session.commit()
                print("Prediction results successfully saved to database")
            except Exception as e:
                db.session.rollback()
                print(f"Error saving prediction results to database: {str(e)}")
                # Continue execution to return results even if saving fails
            
            # Print results to terminal for debugging
            print("\n===== PREDICTION RESULTS =====")
            print(f"Prediction Score: {adjusted_score}%")
            print(f"Risk Level: {risk_level}")
            print(f"Risk Factors: {', '.join(key_factors) if key_factors else 'None identified'}")
            print("Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            print("==============================\n")
            
            return {
                'prediction_score': adjusted_score,
                'prediction_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_level': risk_level,
                'key_factors': key_factors,
                'recommendations': recommendations,
                'used_profile_data': profile_updated,
                'feature_importances': feature_importances
            }, 200
        except Exception as e:
            db.session.rollback()
            print(f"Prediction error: {str(e)}")
            return {'error': str(e)}, 500
    
    def _get_blood_pressure_averages(self, user_id, days=30):
        """Get average blood pressure values from recent readings."""
        try:
            # Get readings from the last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            readings = BloodPressure.query.filter_by(user_id=user_id)\
                .filter(BloodPressure.measurement_date >= start_date)\
                .all()
            
            if not readings:
                print("No BP readings found for user")
                return None
            
            # Calculate averages
            systolic_values = [r.systolic for r in readings if r.systolic]
            diastolic_values = [r.diastolic for r in readings if r.diastolic]
            pulse_values = [r.pulse for r in readings if r.pulse]
            
            if not systolic_values or not diastolic_values:
                print("No valid BP values found in readings")
                return None
            
            return {
                'avg_systolic': sum(systolic_values) / len(systolic_values),
                'avg_diastolic': sum(diastolic_values) / len(diastolic_values),
                'avg_pulse': sum(pulse_values) / len(pulse_values) if pulse_values else None
            }
        except Exception as e:
            print(f"Error calculating BP averages: {str(e)}")
            return None
    
    def _extract_feature_importances(self):
        """Extract feature importances from the model for visualization."""
        try:
            if not hasattr(self.model, 'feature_importances_'):
                return None
                
            # Get feature names or create placeholders
            feature_names = [
                "Gender(Male)", "Smoker", "CigsPerDay", "BPMeds", "Diabetes", 
                "TotalChol", "SysBP", "DiaBP", "BMI", "HeartRate", "Glucose", "Age",
                "KidneyDisease", "HeartDisease", "FamilyHistory", "PhysicalActivity",
                "Alcohol", "SaltIntake", "Stress", "SleepHours"
            ]
            
            # Add text feature placeholders
            for i in range(7):
                feature_names.append(f"TextFeature{i+1}")
            
            # Create a dictionary of feature importances
            importances = self.model.feature_importances_
            if len(importances) != len(feature_names):
                # Truncate to match the shorter length
                min_length = min(len(importances), len(feature_names))
                importances = importances[:min_length]
                feature_names = feature_names[:min_length]
                
            return {name: float(importance) for name, importance in zip(feature_names, importances)}
            
        except Exception as e:
            print(f"Error extracting feature importances: {str(e)}")
            return None
    
    def _update_patient_data_from_profile(self, patient_data, user_profile):
        """Update patient data with values from user profile."""
        updated = False
        
        # Always override with profile data for these fields
        if user_profile.age:
            patient_data.age = user_profile.age
            updated = True
        
        if user_profile.gender:
            patient_data.gender = user_profile.gender
            updated = True
        
        # Calculate BMI from profile if available
        if user_profile.bmi:
            patient_data.bmi = user_profile.bmi
            updated = True
        elif user_profile.weight and user_profile.height:
            # Recalculate BMI just to be sure
            height_in_meters = user_profile.height / 100
            patient_data.bmi = round(user_profile.weight / (height_in_meters * height_in_meters), 2)
            updated = True
        
        # Commit changes to the database if updates were made
        if updated:
            db.session.commit()
            print(f"Updated patient data from user profile: Age={patient_data.age}, Gender={patient_data.gender}, BMI={patient_data.bmi}")
        
        return updated
    
    def _extract_structured_features(self, patient_data):
        """Extract numerical and categorical features."""
        # Print raw values for debugging
        print("\n===== PATIENT DATA =====")
        print(f"Age: {patient_data.age}")
        print(f"Gender: {patient_data.gender}")
        print(f"BP: {patient_data.sys_bp}/{patient_data.dia_bp}")
        print(f"BMI: {patient_data.bmi}")
        print(f"Cholesterol: {patient_data.total_chol}")
        print(f"Smoking: {patient_data.current_smoker}")
        print(f"Diabetes: {patient_data.diabetes}")
        print("=======================\n")
        
        features = []
        
        # Core Framingham features
        features.extend([
            1 if patient_data.gender and patient_data.gender.lower() == 'male' else 0,
            1 if patient_data.current_smoker else 0,
            float(patient_data.cigs_per_day or 0),
            1 if patient_data.bp_meds else 0,
            1 if patient_data.diabetes else 0,
            float(patient_data.total_chol or 0),
            float(patient_data.sys_bp or 0),
            float(patient_data.dia_bp or 0),
            float(patient_data.bmi or 0),
            float(patient_data.heart_rate or 0),
            float(patient_data.glucose or 0),
            float(patient_data.age or 0)
        ])
        
        # Additional features
        features.extend([
            1 if patient_data.kidney_disease else 0,
            1 if patient_data.heart_disease else 0,
            1 if patient_data.family_history_htn else 0,
            self._encode_physical_activity(patient_data.physical_activity_level),
            self._encode_alcohol(patient_data.alcohol_consumption),
            self._encode_salt_intake(patient_data.salt_intake),
            self._encode_stress(patient_data.stress_level),
            float(patient_data.sleep_hours or 0)
        ])
        
        # Print features for debugging
        feature_names = [
            "Gender(Male)", "Smoker", "CigsPerDay", "BPMeds", "Diabetes", 
            "TotalChol", "SysBP", "DiaBP", "BMI", "HeartRate", "Glucose", "Age",
            "KidneyDisease", "HeartDisease", "FamilyHistory", "PhysicalActivity",
            "Alcohol", "SaltIntake", "Stress", "SleepHours"
        ]
        print("\n===== STRUCTURED FEATURES =====")
        for name, value in zip(feature_names, features):
            print(f"{name}: {value}")
        print("==============================\n")
        
        return np.array(features)
    
    def _extract_text_features(self, patient_data, expected_features=7):
        """Extract features from text fields."""
        if not self.vectorizer:
            return np.zeros(expected_features)
        
        text_data = ""
        if patient_data.diet_description:
            text_data += f" Diet: {patient_data.diet_description}"
        if patient_data.medical_history:
            text_data += f" History: {patient_data.medical_history}"
        
        if not text_data.strip():
            return np.zeros(expected_features)
        
        try:
            # Extract features based on medical terminology and diet information
            extracted_features = extract_features_from_text(text_data)
            
            # Transform using vectorizer
            text_features = self.vectorizer.transform([extracted_features]).toarray()[0]
            
            # If we have more features than expected, use feature selection or dimensionality reduction
            if len(text_features) > expected_features:
                # Option 1: Take the first n features
                text_features = text_features[:expected_features]
                
                # Option 2 (alternative): Sum or average features to reduce dimensionality
                # text_features = np.array_split(text_features, expected_features)
                # text_features = np.array([sum(group) for group in text_features])
            
            # If we have fewer features than expected, pad with zeros
            elif len(text_features) < expected_features:
                text_features = np.pad(text_features, (0, expected_features - len(text_features)))
            
            return text_features
        except Exception as e:
            print(f"Error in text feature extraction: {str(e)}")
            return np.zeros(expected_features)
    
    def _encode_physical_activity(self, activity):
        """Encode physical activity level."""
        if not activity:
            return 0
        mapping = {'low': 0, 'moderate': 1, 'high': 2}
        return mapping.get(activity.lower(), 0)
    
    def _encode_alcohol(self, alcohol):
        """Encode alcohol consumption."""
        if not alcohol:
            return 0
        mapping = {'none': 0, 'light': 1, 'moderate': 2, 'heavy': 3}
        return mapping.get(alcohol.lower(), 0)
    
    def _encode_salt_intake(self, salt):
        """Encode salt intake."""
        if not salt:
            return 1  # Default to moderate
        mapping = {'low': 0, 'moderate': 1, 'high': 2}
        return mapping.get(salt.lower(), 1)
    
    def _encode_stress(self, stress):
        """Encode stress level."""
        if not stress:
            return 1  # Default to moderate
        mapping = {'low': 0, 'moderate': 1, 'high': 2}
        return mapping.get(stress.lower(), 1)
    
    def _get_risk_level(self, score):
        """Convert numerical score to risk level."""
        if score < 20:
            return "Low"
        elif score < 50:
            return "Moderate"
        elif score < 80:
            return "High"
        else:
            return "Very High"
    
    def _identify_key_factors(self, patient_data):
        """Identify key risk factors for this patient."""
        # Create dictionary of factors with their severity and importance
        risk_factors = []
        
        # Major clinical risk factors (highest priority)
        if patient_data.diabetes:
            risk_factors.append({"factor": "Diabetes", "severity": 3, "description": "Diabetes significantly increases hypertension risk"})
        
        if patient_data.kidney_disease:
            risk_factors.append({"factor": "Kidney disease", "severity": 3, "description": "Kidney disease significantly increases hypertension risk"})
        
        if patient_data.heart_disease:
            risk_factors.append({"factor": "Heart disease", "severity": 3, "description": "Heart disease significantly increases hypertension risk"})
        
        # Blood pressure indicators
        if patient_data.sys_bp:
            if patient_data.sys_bp >= 140:
                risk_factors.append({"factor": "Elevated systolic blood pressure", "severity": 3, 
                                  "description": f"Systolic BP of {patient_data.sys_bp} mmHg is above normal range"})
            elif patient_data.sys_bp >= 130:
                risk_factors.append({"factor": "Borderline systolic blood pressure", "severity": 2, 
                                  "description": f"Systolic BP of {patient_data.sys_bp} mmHg is in the elevated range"})
        
        if patient_data.dia_bp:
            if patient_data.dia_bp >= 90:
                risk_factors.append({"factor": "Elevated diastolic blood pressure", "severity": 3, 
                                  "description": f"Diastolic BP of {patient_data.dia_bp} mmHg is above normal range"})
            elif patient_data.dia_bp >= 80:
                risk_factors.append({"factor": "Borderline diastolic blood pressure", "severity": 2, 
                                  "description": f"Diastolic BP of {patient_data.dia_bp} mmHg is in the elevated range"})
        
        # Lifestyle factors
        if patient_data.current_smoker:
            risk_factors.append({"factor": "Smoking", "severity": 2, 
                              "description": "Smoking significantly increases cardiovascular risks"})
        
        if patient_data.bmi:
            if patient_data.bmi >= 30:
                risk_factors.append({"factor": "Obesity", "severity": 2, 
                                  "description": f"BMI of {patient_data.bmi:.1f} indicates obesity"})
            elif patient_data.bmi >= 25:
                risk_factors.append({"factor": "Overweight", "severity": 1, 
                                  "description": f"BMI of {patient_data.bmi:.1f} indicates overweight"})
        
        # Other medical factors
        if patient_data.total_chol:
            if patient_data.total_chol >= 240:
                risk_factors.append({"factor": "High cholesterol", "severity": 2, 
                                  "description": f"Total cholesterol of {patient_data.total_chol} mg/dL is high"})
            elif patient_data.total_chol >= 200:
                risk_factors.append({"factor": "Borderline cholesterol", "severity": 1, 
                                  "description": f"Total cholesterol of {patient_data.total_chol} mg/dL is borderline high"})
        
        if patient_data.family_history_htn:
            risk_factors.append({"factor": "Family history of hypertension", "severity": 2, 
                              "description": "Family history increases hypertension risk"})
        
        # Age factor
        if patient_data.age:
            if patient_data.age >= 65:
                risk_factors.append({"factor": "Age over 65", "severity": 2, 
                                  "description": "Advanced age increases hypertension risk"})
            elif patient_data.age >= 55:
                risk_factors.append({"factor": "Age over 55", "severity": 1, 
                                  "description": "Age is a risk factor for hypertension"})
        
        # Lifestyle factors
        if patient_data.physical_activity_level and patient_data.physical_activity_level.lower() == 'low':
            risk_factors.append({"factor": "Low physical activity", "severity": 1})
        
        if patient_data.salt_intake and patient_data.salt_intake.lower() == 'high':
            risk_factors.append({"factor": "High salt intake", "severity": 1})
        
        if patient_data.stress_level and patient_data.stress_level.lower() == 'high':
            risk_factors.append({"factor": "High stress level", "severity": 1})
        
        if patient_data.alcohol_consumption and patient_data.alcohol_consumption.lower() == 'heavy':
            risk_factors.append({"factor": "Heavy alcohol consumption", "severity": 1})
        
        # Sort by severity (highest first)
        risk_factors.sort(key=lambda x: x["severity"], reverse=True)
        
        # If no risk factors were identified
        if not risk_factors:
            if patient_data.age and patient_data.age > 40:
                risk_factors.append({"factor": "Age over 40", "severity": 1, 
                                  "description": "Age is a minor risk factor for hypertension"})
            else:
                risk_factors.append({"factor": "No major risk factors identified", "severity": 0})
        
        # Return just the factor names for the top factors
        return [factor["factor"] for factor in risk_factors[:5]]
    
    def _generate_recommendations(self, patient_data, risk_factors):
        """Generate personalized recommendations based on risk factors."""
        recommendations = []
        
        # Default recommendation for everyone
        recommendations.append("Monitor your blood pressure regularly")
        
        # Blood pressure specific recommendations
        if any("blood pressure" in factor.lower() for factor in risk_factors):
            recommendations.append("Consult with your healthcare provider about blood pressure management")
            recommendations.append("Consider the DASH diet (rich in fruits, vegetables, and low-fat dairy)")
            recommendations.append("Limit sodium intake to less than 2,300 mg per day")
        
        # Weight management recommendations
        if any(factor in ["Obesity", "Overweight"] for factor in risk_factors):
            recommendations.append("Work with a healthcare provider to develop a weight management plan")
            recommendations.append("Aim for 150 minutes of moderate exercise per week")
            recommendations.append("Focus on portion control and whole foods in your diet")
        
        # Smoking recommendations
        if "Smoking" in risk_factors:
            recommendations.append("Quit smoking - talk to your doctor about cessation programs and resources")
            recommendations.append("Avoid secondhand smoke exposure")
        
        # Diabetes recommendations
        if "Diabetes" in risk_factors:
            recommendations.append("Maintain regular blood glucose monitoring")
            recommendations.append("Follow your diabetes management plan as prescribed by your doctor")
            recommendations.append("Consider consulting with a registered dietitian for meal planning")
        
        # Kidney/heart disease recommendations
        if "Kidney disease" in risk_factors or "Heart disease" in risk_factors:
            recommendations.append("Follow up regularly with your specialist for ongoing management")
            recommendations.append("Take all prescribed medications as directed")
            recommendations.append("Monitor and track your symptoms and report changes to your healthcare provider")
        
        # Lifestyle recommendations
        if "Low physical activity" in risk_factors:
            recommendations.append("Gradually increase physical activity to at least 30 minutes daily")
            recommendations.append("Find activities you enjoy to make exercise sustainable")
        
        if "High salt intake" in risk_factors:
            recommendations.append("Read food labels to identify hidden sodium sources")
            recommendations.append("Cook at home more often to control salt content in meals")
        
        if "High stress level" in risk_factors:
            recommendations.append("Practice stress reduction techniques like meditation, deep breathing, or yoga")
            recommendations.append("Consider counseling or therapy if stress is overwhelming")
        
        if "Heavy alcohol consumption" in risk_factors:
            recommendations.append("Reduce alcohol consumption (limit to 1 drink per day for women, 2 for men)")
            recommendations.append("Consider speaking with a healthcare provider about resources for reducing alcohol intake")
        
        # Add general recommendations if list is too short
        if len(recommendations) < 3:
            recommendations.append("Maintain a balanced diet rich in fruits, vegetables, and whole grains")
            recommendations.append("Limit alcohol consumption")
            recommendations.append("Manage stress through relaxation techniques or mindfulness")
        
        # Return unique recommendations (no duplicates)
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:5]  # Return top 5 recommendations
    
    def _apply_medical_rules(self, patient_data, prediction_score):
        """Apply medical knowledge to adjust prediction scores when model gives implausible results."""
        # Base score from model
        score = prediction_score
        
        # Initialize weighted risk factors
        risk_factors = {
            # Major risk factors (higher weights)
            'kidney_disease': {'value': patient_data.kidney_disease, 'weight': 20},
            'heart_disease': {'value': patient_data.heart_disease, 'weight': 20},
            'diabetes': {'value': patient_data.diabetes, 'weight': 15},
            'high_bp': {'value': (patient_data.sys_bp and patient_data.sys_bp > 140) or 
                                 (patient_data.dia_bp and patient_data.dia_bp > 90), 'weight': 15},
            
            # Moderate risk factors
            'elevated_bp': {'value': (patient_data.sys_bp and 130 <= patient_data.sys_bp < 140) or 
                                     (patient_data.dia_bp and 80 <= patient_data.dia_bp < 90), 'weight': 10},
            'smoking': {'value': patient_data.current_smoker, 'weight': 10},
            'obesity': {'value': patient_data.bmi and patient_data.bmi > 30, 'weight': 10},
            'overweight': {'value': patient_data.bmi and 25 <= patient_data.bmi <= 30, 'weight': 5},
            'family_history': {'value': patient_data.family_history_htn, 'weight': 10},
            'high_cholesterol': {'value': patient_data.total_chol and patient_data.total_chol > 240, 'weight': 10},
            'borderline_cholesterol': {'value': patient_data.total_chol and 200 <= patient_data.total_chol <= 240, 'weight': 5},
            
            # Lifestyle factors
            'low_activity': {'value': patient_data.physical_activity_level and 
                                     patient_data.physical_activity_level.lower() == 'low', 'weight': 7},
            'high_salt': {'value': patient_data.salt_intake and 
                                   patient_data.salt_intake.lower() == 'high', 'weight': 7},
            'high_stress': {'value': patient_data.stress_level and 
                                        patient_data.stress_level.lower() == 'high', 'weight': 5},
            'heavy_alcohol': {'value': patient_data.alcohol_consumption and 
                                      patient_data.alcohol_consumption.lower() == 'heavy', 'weight': 7}
        }
        
        # Age is a special case - increases risk with age
        age_risk = 0
        if patient_data.age:
            if patient_data.age >= 65:
                age_risk = 10
            elif patient_data.age >= 55:
                age_risk = 7
            elif patient_data.age >= 45:
                age_risk = 5
            elif patient_data.age >= 35:
                age_risk = 3
        
        # Calculate additional risk based on present factors
        additional_risk = sum(factor['weight'] for factor in risk_factors.values() if factor['value']) + age_risk
        
        # Calculate number of major risk factors (those with weight >= 15)
        major_count = sum(1 for factor in risk_factors.values() 
                         if factor['value'] and factor['weight'] >= 15)
        
        # Set minimum base scores based on risk factor counts
        if major_count >= 2:
            score = max(score, 65)  # At least high risk with 2+ major factors
        elif major_count == 1:
            score = max(score, 45)  # At least moderate risk with 1 major factor
        
        # Apply the additional risk as a percentage of remaining room to 100
        if score < 95:  # Cap at 95 to acknowledge uncertainty
            room_for_increase = 95 - score
            percentage_increase = min(additional_risk / 100, 0.8)  # Cap at 80% of remaining room
            score += room_for_increase * percentage_increase
        
        # Final sanity checks
        if major_count >= 3 and score < 75:
            score = 75  # Minimum score with 3+ major risk factors
        
        # Hard cap at 95
        return min(round(score), 95)
    
    def _generate_mock_prediction(self, patient_data):
        """Generate a mock prediction for testing when model is not available."""
        # Create a realistic mock risk score based on available patient data
        base_score = 35  # Start with a lower baseline risk
        
        # Adjust based on available risk factors with more weight on medical conditions
        if patient_data.age:
            if patient_data.age > 65:
                base_score += 15
            elif patient_data.age > 55:
                base_score += 10
            elif patient_data.age > 45:
                base_score += 5
            elif patient_data.age > 35:
                base_score += 3
        
        # Medical conditions have higher impact
        if patient_data.current_smoker:
            base_score += 10
            if patient_data.cigs_per_day and patient_data.cigs_per_day > 10:
                base_score += 5
        
        if patient_data.diabetes:
            base_score += 15
        
        if patient_data.heart_disease:
            base_score += 18
            
        if patient_data.kidney_disease:
            base_score += 18
            
        if patient_data.family_history_htn:
            base_score += 8
        
        # Blood pressure has significant impact
        if patient_data.sys_bp:
            if patient_data.sys_bp >= 160:
                base_score += 25
            elif patient_data.sys_bp >= 140:
                base_score += 18
            elif patient_data.sys_bp >= 130:
                base_score += 10
            elif patient_data.sys_bp >= 120:
                base_score += 5
                
        if patient_data.dia_bp:
            if patient_data.dia_bp >= 100:
                base_score += 20
            elif patient_data.dia_bp >= 90:
                base_score += 15
            elif patient_data.dia_bp >= 85:
                base_score += 8
            elif patient_data.dia_bp >= 80:
                base_score += 4
        
        # Cholesterol factor
        if patient_data.total_chol:
            if patient_data.total_chol >= 240:
                base_score += 15
            elif patient_data.total_chol >= 200:
                base_score += 8
        
        # Lifestyle factors have smaller but meaningful impact
        if patient_data.physical_activity_level:
            if patient_data.physical_activity_level.lower() == 'low':
                base_score += 6
            elif patient_data.physical_activity_level.lower() == 'moderate':
                base_score += 2
            # High physical activity reduces risk
            elif patient_data.physical_activity_level.lower() == 'high':
                base_score -= 3
        
        if patient_data.salt_intake and patient_data.salt_intake.lower() == 'high':
            base_score += 5
        
        if patient_data.stress_level and patient_data.stress_level.lower() == 'high':
            base_score += 5
        
        if patient_data.alcohol_consumption:
            if patient_data.alcohol_consumption.lower() == 'heavy':
                base_score += 8
            elif patient_data.alcohol_consumption.lower() == 'moderate':
                base_score += 4
        
        # BMI factor
        if patient_data.bmi:
            if patient_data.bmi >= 30:
                base_score += 10
            elif patient_data.bmi >= 25:
                base_score += 5
        
        # Sleep factor
        if patient_data.sleep_hours:
            if patient_data.sleep_hours < 6:
                base_score += 5
        
        # Apply a reasonable cap
        risk_score = min(max(base_score, 10), 95)  # Ensure score is between 10 and 95
        
        # Get risk level based on score
        risk_level = self._get_risk_level(risk_score)
        
        # Get key factors - more personalized based on actual inputs
        key_factors = self._identify_key_factors(patient_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patient_data, key_factors)
        
        # Save mock prediction to database
        try:
            patient_data.prediction_score = risk_score
            patient_data.prediction_date = datetime.utcnow()
            patient_data.risk_level = risk_level
            patient_data.risk_factors = ','.join(key_factors) if key_factors else ''
            patient_data.recommendations = ','.join(recommendations) if recommendations else ''
            db.session.commit()
            print(f"Mock prediction saved to database with score: {risk_score}, level: {risk_level}")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving mock prediction: {str(e)}")
        
        # Return formatted prediction with full details
        return {
            'prediction_score': risk_score,
            'prediction_date': datetime.utcnow().strftime('%A %d %B %Y, %I:%M %p'),
            'risk_level': risk_level,
            'key_factors': key_factors,
            'recommendations': recommendations,
            'is_mock': True,  # Flag to indicate this is mock data
            'used_profile_data': True
        }