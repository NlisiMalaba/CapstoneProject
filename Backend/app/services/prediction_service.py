import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from app.models.patient_data import PatientData
from app.database import db
from app.utils.text_processor import extract_features_from_text

class PredictionService:
    def __init__(self):
        # Load the model and vectorizer
        model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'model.pkl')
        vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'vectorizer.pkl')
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
        except FileNotFoundError:
            # If model doesn't exist yet, set to None - will be created on first use
            self.model = None
            self.vectorizer = None
    
    def save_patient_data(self, user_id, data):
        """Save patient data to database."""
        try:
            # Check if patient data already exists for this user
            existing_data = PatientData.query.filter_by(user_id=user_id).first()
            
            if existing_data:
                # Update existing record
                for key, value in data.items():
                    if hasattr(existing_data, key):
                        setattr(existing_data, key, value)
                existing_data.updated_at = datetime.utcnow()
                patient_data = existing_data
            else:
                # Create new record
                patient_data = PatientData(user_id=user_id, **data)
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
                return {'error': 'Model not trained yet'}, 500
            
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
            
            # Save all prediction results to database
            try:
                # Store basic prediction data
                patient_data.prediction_score = adjusted_score
                patient_data.prediction_date = datetime.utcnow()
                patient_data.risk_level = risk_level
                
                # Store risk factors (as comma-separated string)
                patient_data.risk_factors = ','.join(key_factors) if key_factors else ''
                
                # Store recommendations (as comma-separated string)
                patient_data.recommendations = ','.join(recommendations) if recommendations else ''
                
                # Commit changes to database
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
                'recommendations': recommendations
            }, 200
        except Exception as e:
            db.session.rollback()
            print(f"Prediction error: {str(e)}")
            return {'error': str(e)}, 500
    
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