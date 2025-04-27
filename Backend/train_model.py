"""
Script to train a new hypertension prediction model
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

def create_sample_data():
    """Create a sample dataset for training if actual data is unavailable."""
    print("Generating synthetic data for training...")
    np.random.seed(42)
    
    # Number of samples
    n_samples = 1000
    
    # Generate data
    data = {
        'age': np.random.randint(30, 80, n_samples),
        'gender': np.random.choice(['male', 'female'], n_samples),
        'current_smoker': np.random.choice([0, 1], n_samples),
        'cigs_per_day': np.random.randint(0, 30, n_samples),
        'bp_meds': np.random.choice([0, 1], n_samples),
        'diabetes': np.random.choice([0, 1], n_samples),
        'total_chol': np.random.uniform(150, 300, n_samples),
        'sysBP': np.random.uniform(100, 180, n_samples),
        'diaBP': np.random.uniform(60, 100, n_samples),
        'bmi': np.random.uniform(18, 35, n_samples),
        'heart_rate': np.random.uniform(60, 100, n_samples),
        'glucose': np.random.uniform(70, 150, n_samples),
        'physical_activity_level': np.random.choice(['low', 'moderate', 'high'], n_samples),
        'kidney_disease': np.random.choice([0, 1], n_samples),
        'heart_disease': np.random.choice([0, 1], n_samples),
        'family_history_htn': np.random.choice([0, 1], n_samples),
        'alcohol_consumption': np.random.choice(['none', 'light', 'moderate', 'heavy'], n_samples),
        'salt_intake': np.random.choice(['low', 'moderate', 'high'], n_samples),
        'stress_level': np.random.choice(['low', 'moderate', 'high'], n_samples),
        'sleep_hours': np.random.uniform(4, 10, n_samples)
    }
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Create a synthetic target based on realistic risk factors
    risk_score = (
        df['age'] * 0.3 + 
        (df['current_smoker'] * 15) + 
        (df['diabetes'] * 20) + 
        (df['sysBP'] - 120) * 0.2 + 
        (df['diaBP'] - 80) * 0.2 + 
        (df['bmi'] - 25) * 0.5 + 
        (df['heart_disease'] * 25) +
        (df['kidney_disease'] * 20) +
        (df['family_history_htn'] * 10)
    )
    
    # Normalize to 0-100 range
    risk_score = (risk_score - risk_score.min()) / (risk_score.max() - risk_score.min()) * 100
    
    # Convert to hypertension binary label (1 if risk score > 50)
    df['hypertension'] = (risk_score > 50).astype(int)
    
    return df

def train_model(output_path, data=None):
    """Train a hypertension prediction model and save it to disk."""
    print("Starting model training...")
    
    # If no data provided, create synthetic data
    if data is None:
        data = create_sample_data()
    
    print(f"Dataset shape: {data.shape}")
    print(f"Features: {data.columns.tolist()}")
    
    # Prepare features and target
    X = data.drop(['hypertension'], axis=1)
    y = data['hypertension']
    
    # Get feature names
    feature_names = X.columns.tolist()
    print(f"Feature names: {feature_names}")
    
    # Handle categorical variables
    categorical_cols = X.select_dtypes(include=['object']).columns
    
    # One-hot encode categorical variables
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Standardize numerical features
    scaler = StandardScaler()
    numerical_cols = X.select_dtypes(include=['float64', 'int64']).columns
    X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
    X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])
    
    # Create and train model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    # Create TF-IDF vectorizer for text features (even though not used in this model)
    vectorizer = TfidfVectorizer(max_features=7)
    
    # Save model, scaler, and feature names
    print(f"Saving model to {output_path}")
    # Save in the format expected by the ML service
    model_data = {
        'model': model, 
        'preprocessor': scaler,
        'feature_names': feature_names,
        'vectorizer': vectorizer,
        'categorical_cols': categorical_cols.tolist(),
        'numerical_cols': numerical_cols.tolist()
    }
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the model data
    joblib.dump(model_data, output_path)
    print("Model saved successfully!")
    
    return model

if __name__ == "__main__":
    # Check if a config module is available, otherwise use default path
    try:
        from app.config import current_config
        model_path = current_config.MODEL_PATH
    except ImportError:
        model_dir = os.path.join(os.getcwd(), 'app', 'ml_model')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, 'model.pkl')
    
    print(f"Will save model to: {model_path}")
    
    # Train and save model
    train_model(model_path) 