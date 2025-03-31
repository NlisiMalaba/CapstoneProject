from app.database import db
from app.models.medication import Medication
from app.models.medication_reminder import MedicationReminder
from app.models.medication_log import MedicationLog
from app.models.user import User
from datetime import datetime, timedelta
import json
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import SQLAlchemyError

def create_medication(user_id, data):
    """Create a new medication for a user."""
    try:
        # Validate required fields
        required_fields = ['name', 'dosage', 'frequency', 'time_of_day', 'start_date']
        for field in required_fields:
            if field not in data:
                return {'error': f'Missing required field: {field}'}
        
        # Create new medication
        medication = Medication(
            user_id=user_id,
            name=data['name'],
            dosage=data['dosage'],
            frequency=data['frequency'],
            time_of_day=data['time_of_day'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data and data['end_date'] else None,
            notes=data.get('notes')
        )
        
        db.session.add(medication)
        db.session.commit()
        
        return {
            'id': medication.id,
            'message': 'Medication created successfully'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}
    except ValueError as e:
        return {'error': f'Invalid date format: {str(e)}'}

def get_medications(user_id):
    """Get all medications for a user."""
    try:
        medications = Medication.query.filter_by(user_id=user_id).all()
        result = []
        
        for med in medications:
            result.append({
                'id': med.id,
                'name': med.name,
                'dosage': med.dosage,
                'frequency': med.frequency,
                'time_of_day': med.time_of_day,
                'start_date': med.start_date.strftime('%Y-%m-%d'),
                'end_date': med.end_date.strftime('%Y-%m-%d') if med.end_date else None,
                'notes': med.notes,
                'created_at': med.created_at.isoformat()
            })
        
        return result
    except SQLAlchemyError as e:
        return {'error': str(e)}

def get_medication(medication_id, user_id):
    """Get details of a specific medication."""
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        
        if not medication:
            return {'error': 'Medication not found'}
        
        # Get reminders
        reminders = MedicationReminder.query.filter_by(medication_id=medication.id).all()
        reminder_list = []
        
        for reminder in reminders:
            reminder_list.append({
                'id': reminder.id,
                'reminder_time': reminder.reminder_time.isoformat(),
                'phone_number': reminder.phone_number,
                'is_sent': reminder.is_sent,
                'sent_at': reminder.sent_at.isoformat() if reminder.sent_at else None
            })
        
        # Get logs
        logs = MedicationLog.query.filter_by(medication_id=medication.id).order_by(MedicationLog.scheduled_time.desc()).limit(10).all()
        log_list = []
        
        for log in logs:
            log_list.append({
                'id': log.id,
                'status': log.status,
                'scheduled_time': log.scheduled_time.isoformat(),
                'taken_at': log.taken_at.isoformat() if log.taken_at else None,
                'notes': log.notes
            })
        
        return {
            'id': medication.id,
            'name': medication.name,
            'dosage': medication.dosage,
            'frequency': medication.frequency,
            'time_of_day': medication.time_of_day,
            'start_date': medication.start_date.strftime('%Y-%m-%d'),
            'end_date': medication.end_date.strftime('%Y-%m-%d') if medication.end_date else None,
            'notes': medication.notes,
            'created_at': medication.created_at.isoformat(),
            'updated_at': medication.updated_at.isoformat(),
            'reminders': reminder_list,
            'recent_logs': log_list
        }
    except SQLAlchemyError as e:
        return {'error': str(e)}

def update_medication(medication_id, user_id, data):
    """Update a medication."""
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        
        if not medication:
            return {'error': 'Medication not found'}
        
        # Update fields if provided
        if 'name' in data:
            medication.name = data['name']
        if 'dosage' in data:
            medication.dosage = data['dosage']
        if 'frequency' in data:
            medication.frequency = data['frequency']
        if 'time_of_day' in data:
            medication.time_of_day = data['time_of_day']
        if 'start_date' in data:
            medication.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            medication.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data['end_date'] else None
        if 'notes' in data:
            medication.notes = data['notes']
        
        db.session.commit()
        
        return {
            'id': medication.id,
            'message': 'Medication updated successfully'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}
    except ValueError as e:
        return {'error': f'Invalid date format: {str(e)}'}

def delete_medication(medication_id, user_id):
    """Delete a medication."""
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        
        if not medication:
            return {'error': 'Medication not found'}
        
        db.session.delete(medication)
        db.session.commit()
        
        return {'message': 'Medication deleted successfully'}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}

def create_reminder(medication_id, user_id, data):
    """Create a reminder for a medication."""
    try:
        # Validate required fields
        required_fields = ['reminder_time', 'phone_number']
        for field in required_fields:
            if field not in data:
                return {'error': f'Missing required field: {field}'}
        
        # Validate medication exists and belongs to user
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        if not medication:
            return {'error': 'Medication not found'}
        
        # Create new reminder
        reminder = MedicationReminder(
            medication_id=medication_id,
            reminder_time=datetime.fromisoformat(data['reminder_time']),
            phone_number=data['phone_number'],
            verification_code=''
        )
        
        # Generate verification code
        reminder.generate_verification_code()
        
        db.session.add(reminder)
        db.session.commit()
        
        return {
            'id': reminder.id,
            'message': 'Reminder created successfully'
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}
    except ValueError as e:
        return {'error': f'Invalid date format: {str(e)}'}

def get_reminders(medication_id, user_id):
    """Get all reminders for a medication."""
    try:
        # Validate medication exists and belongs to user
        medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()
        if not medication:
            return {'error': 'Medication not found'}
        
        reminders = MedicationReminder.query.filter_by(medication_id=medication_id).all()
        result = []
        
        for reminder in reminders:
            result.append({
                'id': reminder.id,
                'reminder_time': reminder.reminder_time.isoformat(),
                'phone_number': reminder.phone_number,
                'is_sent': reminder.is_sent,
                'sent_at': reminder.sent_at.isoformat() if reminder.sent_at else None,
                'created_at': reminder.created_at.isoformat()
            })
        
        return result
    except SQLAlchemyError as e:
        return {'error': str(e)}

def verify_medication_taken(user_id, data):
    """Verify medication was taken using verification code."""
    try:
        if 'verification_code' not in data:
            return {'error': 'Verification code is required'}
        
        # Find the reminder with this verification code
        reminder = MedicationReminder.query.filter_by(verification_code=data['verification_code']).first()
        
        if not reminder:
            return {'error': 'Invalid verification code'}
        
        # Verify the medication belongs to the user
        medication = Medication.query.filter_by(id=reminder.medication_id).first()
        if not medication or medication.user_id != user_id:
            return {'error': 'Invalid verification code'}
        
        # Check if the code has expired
        if reminder.expires_at and reminder.expires_at < datetime.utcnow():
            return {'error': 'Verification code has expired'}
        
        # Create medication log
        log = MedicationLog(
            medication_id=reminder.medication_id,
            reminder_id=reminder.id,
            status='taken',
            taken_at=datetime.utcnow(),
            scheduled_time=reminder.reminder_time,
            verification_code=reminder.verification_code,
            notes=data.get('notes')
        )
        
        db.session.add(log)
        db.session.commit()
        
        return {
            'message': 'Medication verified as taken',
            'medication_name': medication.name
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}

def get_medication_analytics(user_id, start_date=None, end_date=None):
    """Get medication adherence analytics."""
    try:
        query = MedicationLog.query.join(
            Medication, Medication.id == MedicationLog.medication_id
        ).filter(Medication.user_id == user_id)
        
        # Apply date filters if provided
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(MedicationLog.scheduled_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(MedicationLog.scheduled_time < end_datetime)
        
        logs = query.all()
        
        # Calculate overall statistics
        total_reminders = len(logs)
        taken_count = sum(1 for log in logs if log.status == 'taken')
        missed_count = sum(1 for log in logs if log.status == 'missed')
        adherence_rate = (taken_count / total_reminders) * 100 if total_reminders > 0 else 0
        
        # Group by medication
        medication_stats = {}
        for log in logs:
            med_id = log.medication_id
            if med_id not in medication_stats:
                medication = Medication.query.get(med_id)
                medication_stats[med_id] = {
                    'name': medication.name,
                    'total': 0,
                    'taken': 0,
                    'missed': 0,
                    'adherence_rate': 0
                }
            
            medication_stats[med_id]['total'] += 1
            if log.status == 'taken':
                medication_stats[med_id]['taken'] += 1
            elif log.status == 'missed':
                medication_stats[med_id]['missed'] += 1
        
        # Calculate adherence rate for each medication
        for med_id in medication_stats:
            med_total = medication_stats[med_id]['total']
            med_taken = medication_stats[med_id]['taken']
            medication_stats[med_id]['adherence_rate'] = (med_taken / med_total) * 100 if med_total > 0 else 0
        
        return {
            'overall': {
                'total_reminders': total_reminders,
                'taken_count': taken_count,
                'missed_count': missed_count,
                'adherence_rate': adherence_rate
            },
            'by_medication': list(medication_stats.values())
        }
    except SQLAlchemyError as e:
        return {'error': str(e)}
    except ValueError as e:
        return {'error': f'Invalid date format: {str(e)}'}

def mark_missed_medications():
    """Mark medications as missed if not taken after expiry."""
    try:
        # Find all reminders that have expired but don't have logs
        current_time = datetime.utcnow()
        expired_reminders = MedicationReminder.query.filter(
            MedicationReminder.expires_at < current_time,
            ~MedicationReminder.id.in_(
                db.session.query(MedicationLog.reminder_id).filter(MedicationLog.reminder_id.isnot(None))
            )
        ).all()
        
        for reminder in expired_reminders:
            # Create missed log
            log = MedicationLog(
                medication_id=reminder.medication_id,
                reminder_id=reminder.id,
                status='missed',
                taken_at=None,
                scheduled_time=reminder.reminder_time,
                verification_code=reminder.verification_code,
                notes='Automatically marked as missed'
            )
            
            db.session.add(log)
        
        db.session.commit()
        return {'message': f'Marked {len(expired_reminders)} medications as missed'}
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)} 