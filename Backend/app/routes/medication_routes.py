from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.medication import Medication
from app.models.medication_reminder import MedicationReminder
from app.models.medication_log import MedicationLog
from app.controllers.medication_controller import (
    create_medication, 
    get_medications, 
    get_medication, 
    update_medication, 
    delete_medication,
    create_reminder,
    get_reminders,
    verify_medication_taken,
    get_medication_analytics
)

medication_bp = Blueprint('medication', __name__, url_prefix='/api/medications')

@medication_bp.route('', methods=['POST'])
@jwt_required()
def add_medication():
    """
    Add a new medication
    ---
    tags:
      - Medications
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - dosage
              - frequency
              - time_of_day
              - start_date
            properties:
              name:
                type: string
                description: Name of the medication
              dosage:
                type: string
                description: Dosage information
              frequency:
                type: string
                description: Frequency of taking medication
              time_of_day:
                type: string
                description: JSON string of times to take medication
              start_date:
                type: string
                format: date
                description: Date to start medication
              end_date:
                type: string
                format: date
                description: Date to end medication (optional)
              notes:
                type: string
                description: Additional notes (optional)
    responses:
      201:
        description: Medication created successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    result = create_medication(user_id, data)
    
    if 'error' in result:
        return jsonify(result), 400
        
    return jsonify(result), 201

@medication_bp.route('', methods=['GET'])
@jwt_required()
def list_medications():
    """
    Get all medications for the authenticated user
    ---
    tags:
      - Medications
    security:
      - JWT: []
    responses:
      200:
        description: List of medications
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    medications = get_medications(user_id)
    return jsonify(medications), 200

@medication_bp.route('/<int:medication_id>', methods=['GET'])
@jwt_required()
def get_medication_details(medication_id):
    """
    Get details of a specific medication
    ---
    tags:
      - Medications
    security:
      - JWT: []
    parameters:
      - name: medication_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Medication details
      404:
        description: Medication not found
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    result = get_medication(medication_id, user_id)
    
    if 'error' in result:
        return jsonify(result), 404
        
    return jsonify(result), 200

@medication_bp.route('/<int:medication_id>', methods=['PUT'])
@jwt_required()
def update_medication_details(medication_id):
    """
    Update a medication
    ---
    tags:
      - Medications
    security:
      - JWT: []
    parameters:
      - name: medication_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
              dosage:
                type: string
              frequency:
                type: string
              time_of_day:
                type: string
              start_date:
                type: string
                format: date
              end_date:
                type: string
                format: date
              notes:
                type: string
    responses:
      200:
        description: Medication updated successfully
      400:
        description: Invalid request data
      404:
        description: Medication not found
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    result = update_medication(medication_id, user_id, data)
    
    if 'error' in result:
        if 'not found' in result['error']:
            return jsonify(result), 404
        return jsonify(result), 400
        
    return jsonify(result), 200

@medication_bp.route('/<int:medication_id>', methods=['DELETE'])
@jwt_required()
def remove_medication(medication_id):
    """
    Delete a medication
    ---
    tags:
      - Medications
    security:
      - JWT: []
    parameters:
      - name: medication_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Medication deleted successfully
      404:
        description: Medication not found
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    result = delete_medication(medication_id, user_id)
    
    if 'error' in result:
        return jsonify(result), 404
        
    return jsonify(result), 200

@medication_bp.route('/<int:medication_id>/reminders', methods=['POST'])
@jwt_required()
def add_reminder(medication_id):
    """
    Add a reminder for a medication
    ---
    tags:
      - Reminders
    security:
      - JWT: []
    parameters:
      - name: medication_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - reminder_time
              - phone_number
            properties:
              reminder_time:
                type: string
                format: date-time
                description: Time to send the reminder
              phone_number:
                type: string
                description: Phone number to send SMS
    responses:
      201:
        description: Reminder created successfully
      400:
        description: Invalid request data
      404:
        description: Medication not found
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    result = create_reminder(medication_id, user_id, data)
    
    if 'error' in result:
        if 'not found' in result['error']:
            return jsonify(result), 404
        return jsonify(result), 400
        
    return jsonify(result), 201

@medication_bp.route('/<int:medication_id>/reminders', methods=['GET'])
@jwt_required()
def list_reminders(medication_id):
    """
    Get all reminders for a medication
    ---
    tags:
      - Reminders
    security:
      - JWT: []
    parameters:
      - name: medication_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of reminders
      404:
        description: Medication not found
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    result = get_reminders(medication_id, user_id)
    
    if 'error' in result:
        return jsonify(result), 404
        
    return jsonify(result), 200

@medication_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_medication():
    """
    Verify medication was taken using verification code
    ---
    tags:
      - Medications
    security:
      - JWT: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - verification_code
            properties:
              verification_code:
                type: string
                description: Verification code from SMS
              notes:
                type: string
                description: Optional notes about taking the medication
    responses:
      200:
        description: Medication verified as taken
      400:
        description: Invalid verification code
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    result = verify_medication_taken(user_id, data)
    
    if 'error' in result:
        return jsonify(result), 400
        
    return jsonify(result), 200

@medication_bp.route('/analytics', methods=['GET'])
@jwt_required()
def medication_analytics():
    """
    Get medication adherence analytics
    ---
    tags:
      - Medications
    security:
      - JWT: []
    parameters:
      - name: start_date
        in: query
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        schema:
          type: string
          format: date
    responses:
      200:
        description: Medication adherence analytics
      401:
        description: Unauthorized
    """
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    result = get_medication_analytics(user_id, start_date, end_date)
    return jsonify(result), 200 