import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ml_service import HypertensionModel

def test_model_performance():
    """Test the hypertension prediction model's performance"""
    print("Testing hypertension prediction model...")
    
    # Load and preprocess data
    data_path = "../data/hypertension.csv"
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return
    
    # Initialize model
    model = HypertensionModel()
    
    # Preprocess data
    df = model.preprocess_data(data_path)
    
    # Define features and target
    feature_cols = ["gender", "currentSmoker", "cigsPerDay", "BPMeds", 
                   "diabetes", "totlChol", "BMI", "heartRate", "glucose"]
    X = df[feature_cols].copy()
    
    # Convert gender to numeric
    if "gender" in X.columns:
        X["gender"] = X["gender"].map({"M": 0, "F": 1})
    
    y = df["hypertension"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train model
    model.train_model(data_path)
    
    # Make predictions on test set
    test_data = []
    for idx, row in X_test.iterrows():
        patient_data = {
            "gender": "F" if row["gender"] == 1 else "M",
            "current_smoker": bool(row["currentSmoker"]),
            "cigs_per_day": row["cigsPerDay"],
            "bp_meds": bool(row["BPMeds"]),
            "diabetes": bool(row["diabetes"]),
            "total_cholesterol": row["totlChol"],
            "bmi": row["BMI"],
            "heart_rate": row["heartRate"],
            "glucose": row["glucose"],
        }
        test_data.append(patient_data)
    
    # Get predictions
    predictions = []
    for data in test_data:
        result = model.predict(data)
        predictions.append(1 if result["score"] > 50 else 0)
    
    # Calculate metrics
    cm = confusion_matrix(y_test, predictions)
    report = classification_report(y_test, predictions)
    
    # Try to calculate ROC AUC
    try:
        roc_auc = roc_auc_score(y_test, predictions)
        print(f"ROC AUC Score: {roc_auc:.4f}")
    except:
        print("Could not calculate ROC AUC score")
    
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)
    
    return {
        "confusion_matrix": cm.tolist(),
        "classification_report": report
    }

if __name__ == "__main__":
    test_model_performance()