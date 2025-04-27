"""
Test script to verify the ML model is working correctly
"""
import os
import sys
from app.main import create_app
from app.services.ml_service import hypertension_prediction_service
from app.services.prediction_service import PredictionService

def test_model():
    print("\n=== Testing Hypertension Model ===\n")
    
    # Create app context
    app = create_app('development')
    
    with app.app_context():
        # 1. Check model path and existence
        print("\n== Checking model file ==")
        model_path = hypertension_prediction_service.model_path
        print(f"Model path: {model_path}")
        
        if os.path.exists(model_path):
            print(f"✓ Model file exists with size: {os.path.getsize(model_path)} bytes")
        else:
            print(f"✗ Model file does not exist at path: {model_path}")
            # Check common locations
            possible_paths = [
                os.path.join(os.getcwd(), 'app', 'ml_model', 'model.pkl'),
                os.path.join(os.getcwd(), 'ml_model', 'model.pkl'),
                os.path.join(os.getcwd(), 'Backend', 'app', 'ml_model', 'model.pkl')
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"  Found model at alternative path: {path}")
                    print(f"  Consider updating MODEL_PATH config to point to this location")
        
        # 2. Try loading the model
        print("\n== Trying to load model ==")
        if hypertension_prediction_service.model is None:
            print("Model not yet loaded, attempting to load...")
            success = hypertension_prediction_service.load_model()
            if success:
                print(f"✓ Model loaded successfully")
            else:
                print(f"✗ Failed to load model")
        else:
            print(f"✓ Model already loaded")
        
        # 3. Check model attributes
        print("\n== Checking model attributes ==")
        if hypertension_prediction_service.model:
            print(f"Model type: {type(hypertension_prediction_service.model).__name__}")
            print(f"Feature names available: {hypertension_prediction_service.feature_names is not None}")
            if hypertension_prediction_service.feature_names:
                print(f"Number of features: {len(hypertension_prediction_service.feature_names)}")
                print(f"First few features: {hypertension_prediction_service.feature_names[:5]}")
        else:
            print("✗ Model not available to check attributes")
        
        # 4. Test with sample data
        print("\n== Testing prediction with sample data ==")
        
        # Create a sample with all values for complete testing
        sample_data = {
            'age': 55,
            'gender': 'male',
            'current_smoker': True,
            'cigs_per_day': 10,
            'bp_meds': False,
            'diabetes': False,
            'total_chol': 220,
            'sys_bp': 140,
            'dia_bp': 90,
            'bmi': 28.5,
            'heart_rate': 80,
            'glucose': 90,
            'physical_activity_level': 'moderate',
            'kidney_disease': False,
            'heart_disease': False,
            'family_history_htn': True,
            'alcohol_consumption': 'moderate',
            'salt_intake': 'high',
            'stress_level': 'moderate',
            'sleep_hours': 7
        }
        
        try:
            result = hypertension_prediction_service.predict(sample_data)
            print(f"✓ Prediction successful")
            print(f"Prediction score: {result['prediction_score']}%")
            print(f"Risk level: {result['prediction_label']}")
        except Exception as e:
            print(f"✗ Prediction failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 5. Test PredictionService using mock data
        print("\n== Testing PredictionService with mock data ==")
        from app.models.patient_data import PatientData
        
        # Create a mock patient data object
        mock_patient = PatientData(
            user_id=1,
            age=60,
            gender='female',
            current_smoker=False,
            sys_bp=130,
            dia_bp=85,
            bmi=26.0
        )
        
        prediction_service = PredictionService()
        print(f"Model available in service: {prediction_service.model is not None}")
        
        try:
            result, status = prediction_service.predict_hypertension(mock_patient)
            print(f"Status code: {status}")
            if status == 200:
                print(f"✓ Prediction successful")
                print(f"Prediction score: {result['prediction_score']}%")
                print(f"Risk level: {result['risk_level']}")
                print(f"Used mock prediction: {result.get('is_mock', False)}")
            else:
                print(f"✗ Prediction failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"✗ Prediction service failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    test_model() 