import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import pickle
import os
from app.utils.text_processor import extract_features_from_text

def prepare_data(csv_path):
    """Load and prepare data from CSV."""
    # Load data
    df = pd.read_csv(csv_path)
    
    # Basic preprocessing
    df.fillna(0, inplace=True)
    
    # Define target variable (assuming we need to create it from BP values)
    # Hypertension defined as systolic BP >= 140 or diastolic BP >= 90
    df['hypertension'] = ((df['sysBP'] >= 140) | (df['diaBP'] >= 90)).astype(int)
    
    # Add synthetic text data for demo purposes
    np.random.seed(42)
    diet_options = [
        "High salt diet with processed foods", 
        "Low sodium Mediterranean diet with vegetables and fish",
        "Balanced diet with moderate salt intake",
        "High protein diet with moderate salt",
        "Vegetarian diet with occasional dairy"
    ]
    
    medical_options = [
        "No significant medical history",
        "Family history of hypertension",
        "Previous kidney issues, no medication",
        "Prior cardiac event, on medication",
        "Diabetes type 2, well controlled"
    ]
    
    df['diet_description'] = np.random.choice(diet_options, size=len(df))
    df['medical_history'] = np.random.choice(medical_options, size=len(df))
    
    # Process text data
    df['text_features'] = df.apply(
        lambda row: extract_features_from_text(f"{row['diet_description']} {row['medical_history']}"), 
        axis=1
    )
    
    return df

def train_model(df, model_output_path='app/ml_model/'):
    """Train ML model using prepared data."""
    # Extract features and target
    X_text = df['text_features'].fillna('')
    
    # Create vectorizer for text features
    vectorizer = TfidfVectorizer(max_features=100)
    X_text_vect = vectorizer.fit_transform(X_text).toarray()
    
    # Numerical features
    X_num = df[['gender', 'currentSmoker', 'cigsPerDay', 'BPMeds', 'diabetes', 
                'totlChol', 'sysBP', 'diaBP', 'BMI', 'heartRate', 'glucose']].values
    
    # Combine features
    X = np.hstack([X_num, X_text_vect])
    y = df['hypertension'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'auc': roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    }
    
    # Save model and vectorizer
    os.makedirs(model_output_path, exist_ok=True)
    
    with open(os.path.join(model_output_path, 'model.pkl'), 'wb') as f:
        pickle.dump(model, f)
    
    with open(os.path.join(model_output_path, 'vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)
    
    return model, vectorizer, metrics