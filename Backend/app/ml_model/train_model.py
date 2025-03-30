import os
import sys
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.ml_utils import prepare_data, train_model

def main():
    """Train and save the ML model."""
    # Path to CSV file
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           'data', 'hypertension.csv')
    
    print(f"Looking for data file at: {csv_path}")
    
    if not os.path.exists(csv_path):
        print("Data file not found. Creating synthetic data for demonstration.")
        create_synthetic_data(csv_path)
    
    # Load and prepare data
    print("Preparing data...")
    df = prepare_data(csv_path)
    
    # Train model
    print("Training model...")
    model, vectorizer, metrics = train_model(df)
    
    # Print metrics
    print("\nModel Performance:")
    for metric, value in metrics.items():
        print(f"{metric.capitalize()}: {value:.4f}")
    
    print("\nModel and vectorizer saved successfully!")

def create_synthetic_data(output_path):
    """Create synthetic data for demonstration purposes."""
    import numpy as np
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    # Create dataframe
    df = pd.DataFrame({
        'gender': np.random.choice([0, 1], size=n_samples),  # 0=female, 1=male
        'currentSmoker': np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]),
        'cigsPerDay': np.random.choice(range(0, 41), size=n_samples),
        'BPMeds': np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2]),
        'diabetes': np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1]),
        'totlChol': np.random.normal(200, 30, n_samples),
        'sysBP': np.random.normal(130, 20, n_samples),
        'diaBP': np.random.normal(80, 10, n_samples),
        'BMI': np.random.normal(26, 4, n_samples),
        'heartRate': np.random.normal(75, 10, n_samples),
        'glucose': np.random.normal(85, 20, n_samples)
    })
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Synthetic data created and saved to {output_path}")

if __name__ == "__main__":
    main()