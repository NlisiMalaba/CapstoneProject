import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from typing import Dict, List, Tuple, Any, Optional

from app.config import current_config

class HypertensionPredictionService:
    def __init__(self):
        self.model_path = current_config.MODEL_PATH
        self.model = None
        self.scaler = None
        self.preprocessor = None
        self.feature_names = None
        self.vectorizer = None
        print(self.feature_names)
        
    def load_model(self):
        """Load the trained model from disk."""
        try:
            print(f"Attempting to load model from: {self.model_path}")
            
            if not os.path.exists(self.model_path):
                print(f"Model file does not exist at path: {self.model_path}")
                return False
            
            print(f"Model file exists with size: {os.path.getsize(self.model_path)} bytes")
            model_data = joblib.load(self.model_path)
            
            print(f"Model data loaded with keys: {list(model_data.keys())}")
            self.model = model_data.get('model')
            self.preprocessor = model_data.get('preprocessor')
            self.feature_names = model_data.get('feature_names')
            self.vectorizer = model_data.get('vectorizer', TfidfVectorizer())
            
            print(f"Model loaded: {self.model is not None}")
            print(f"Feature names: {self.feature_names[:5]}... (showing first 5)")
            
            return self.model is not None
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def train_model(self, dataset_path: str = None):
        """Train a new hypertension prediction model."""
        if dataset_path is None:
            dataset_path = current_config.DATASET_PATH
            
        # Load dataset
        data = pd.read_csv(dataset_path)
        
        # Define features and target
        # Basic features from dataset
        X = data.drop(['hypertension'], axis=1) if 'hypertension' in data.columns else data
        
        # If we don't have a target column, we need to create one
        # For this example, we'll define hypertension as sysBP >= 140 or diaBP >= 90
        if 'hypertension' not in data.columns:
            data['hypertension'] = ((data['sysBP'] >= 140) | (data['diaBP'] >= 90)).astype(int)
            
        y = data['hypertension']
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Initialize text vectorizer
        self.vectorizer = TfidfVectorizer(max_features=7)
        
        # Split data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        
        # Preprocessing for numerical features
        numerical_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Preprocessing for categorical features
        categorical_features = X.select_dtypes(include=['object', 'bool']).columns.tolist()
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine preprocessing steps
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Create and train the model pipeline
        model_pipeline = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('classifier', GradientBoostingClassifier(random_state=42))
        ])
        
        # Train the model
        model_pipeline.fit(X_train, y_train)
        
        # Extract the trained model
        self.model = model_pipeline.named_steps['classifier']
        
        # Evaluate the model
        y_pred = model_pipeline.predict(X_test)
        
        # Save the model and preprocessor
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'preprocessor': self.preprocessor,
            'feature_names': self.feature_names,
            'vectorizer': self.vectorizer
        }, self.model_path)
        
        # Return model metrics
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred)
        }
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a hypertension prediction for a patient."""
        # Ensure model is loaded
        if self.model is None:
            self.load_model()
            
        print("Expected features:", self.feature_names)  # Debug
        print("Received features:", list(patient_data.keys()))  # Debug
        
        # Prepare data for prediction
        df = pd.DataFrame([patient_data])
        
        # Ensure all expected features are present
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = None
        
        # Align columns with model's expected features
        df = df[self.feature_names]
        
        # Preprocess the data
        X_processed = self.preprocessor.transform(df)
        
        # Make prediction
        probability = self.model.predict_proba(X_processed)[0, 1]
        
        # Convert to score out of 100
        score = round(probability * 100)
        
        # Get feature importances
        importances = self.get_feature_importances(df)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(probability, patient_data)
        
        return {
            'prediction_score': score,
            'prediction_probability': float(probability),
            'prediction_label': 'High Risk' if probability >= 0.5 else 'Low Risk',
            'feature_importances': importances,
            'recommendations': recommendations
        }
    
    def get_feature_importances(self, data: pd.DataFrame) -> Dict[str, float]:
        """Get feature importances for the prediction."""
        # Transform feature names to match preprocessed features
        transformed_features = []
        
        # For numerical features (direct mapping)
        numerical_features = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
        transformed_features.extend(numerical_features)
        
        # For categorical features (expanded with one-hot encoding)
        categorical_features = data.select_dtypes(include=['object', 'bool']).columns.tolist()
        for feature in categorical_features:
            values = data[feature].dropna().unique()
            for value in values:
                transformed_features.append(f"{feature}_{value}")
        
        # Get importances from model
        importances = self.model.feature_importances_
        
        # Match importances to features
        # Note: This is a simplification - may need adjustment based on actual preprocessing
        importance_dict = {}
        for i, importance in enumerate(importances):
            if i < len(transformed_features):
                importance_dict[transformed_features[i]] = float(importance)
        
        # Sort by importance
        sorted_importances = {k: v for k, v in sorted(
            importance_dict.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_importances
    
    def generate_recommendations(self, probability: float, patient_data: Dict[str, Any]) -> str:
        """Generate recommendations based on prediction and patient data."""
        recommendations = []
        
        # High-level risk assessment
        if probability < 0.2:
            risk_level = "Your hypertension risk is low."
        elif probability < 0.5:
            risk_level = "Your hypertension risk is moderate."
        elif probability < 0.8:
            risk_level = "Your hypertension risk is high."
        else:
            risk_level = "Your hypertension risk is very high."
        
        recommendations.append(risk_level)
        
        # Specific recommendations based on patient data
        if patient_data.get('current_smoker'):
            recommendations.append("Quitting smoking can significantly lower your blood pressure.")
        
        if patient_data.get('bmi', 0) >= 25:
            recommendations.append("Weight management could help reduce your hypertension risk.")
        
        if patient_data.get('sys_bp', 0) >= 130 or patient_data.get('dia_bp', 0) >= 80:
            recommendations.append("Your blood pressure is elevated. Regular monitoring is recommended.")
        
        if patient_data.get('physical_activity_level') in ['low', 'none']:
            recommendations.append("Increasing physical activity can help lower blood pressure.")
        
        if patient_data.get('total_cholesterol', 0) > 200:
            recommendations.append("Your cholesterol is elevated. Consider dietary changes and consult your doctor.")
        
        # General recommendations
        recommendations.append("Consider the DASH diet (low sodium, high in fruits and vegetables).")
        recommendations.append("Limit alcohol consumption to reduce hypertension risk.")
        recommendations.append("Regular check-ups with your healthcare provider are important for monitoring blood pressure.")
        
        return "\n".join(recommendations)

# Singleton instance
hypertension_prediction_service = HypertensionPredictionService()