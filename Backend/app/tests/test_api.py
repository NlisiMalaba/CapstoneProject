import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_read_main():
    """Test the main endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Hypertension Prediction API"}

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 201
    assert "message" in response.json()

def test_login():
    """Test user login"""
    # First register a user if not already registered
    try:
        client.post(
            "/auth/register",
            json={
                "username": "logintest",
                "email": "login@example.com",
                "password": "testpassword"
            }
        )
    except:
        pass
    
    # Now try to login
    response = client.post(
        "/auth/token",
        data={
            "username": "logintest",
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_prediction_flow():
    """Test the prediction workflow"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "predictionuser",
            "email": "prediction@example.com",
            "password": "testpassword"
        }
    )
    
    login_response = client.post(
        "/auth/token",
        data={
            "username": "predictionuser",
            "password": "testpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    access_token = login_response.json()["access_token"]
    
    # Create a prediction
    prediction_response = client.post(
        "/prediction/",
        json={
            "age": 55,
            "gender": "M",
            "current_smoker": True,
            "cigs_per_day": 10,
            "bp_meds": False,
            "diabetes": True,
            "total_cholesterol": 240,
            "sys_bp": 150,
            "dia_bp": 95,
            "bmi": 32,
            "heart_rate": 80,
            "glucose": 120,
            "diet_description": "High sodium diet with processed foods",
            "medical_history": "Family history of heart disease",
            "physical_activity_level": "Sedentary",
            "kidney_disease": False,
            "heart_disease": False
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert prediction_response.status_code == 201
    assert "score" in prediction_response.json()
    assert "risk_level" in prediction_response.json()
    
    # Get the prediction ID
    prediction_id = prediction_response.json()["id"]
    
    # Fetch the prediction
    get_prediction_response = client.get(
        f"/prediction/{prediction_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert get_prediction_response.status_code == 200
    assert get_prediction_response.json()["id"] == prediction_id
    
    # List predictions
    list_predictions_response = client.get(
        "/prediction/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert list_predictions_response.status_code == 200
    assert len(list_predictions_response.json()) > 0

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])