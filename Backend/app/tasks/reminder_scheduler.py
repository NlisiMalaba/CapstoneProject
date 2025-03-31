from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import db
from app.models.medication_reminder import MedicationReminder
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.services.sms_service import sms_service
from app.controllers.medication_controller import mark_missed_medications
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ReminderScheduler:
    """Scheduler for sending medication reminders."""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = BackgroundScheduler()
        
        # Add jobs
        self.scheduler.add_job(
            self.process_reminders,
            IntervalTrigger(minutes=1),
            id='process_reminders',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.process_expired_reminders,
            IntervalTrigger(minutes=30),
            id='process_expired_reminders',
            replace_existing=True
        )
    
    def init_app(self, app):
        """Initialize with Flask app context."""
        self.app = app
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Reminder scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler shutdown")
    
    def process_reminders(self):
        """Process pending reminders and send SMS."""
        with self.app.app_context():
            try:
                logger.info("Processing reminders")
                
                # Find reminders that need to be sent
                # - scheduled within the next minute
                # - not already sent
                now = datetime.utcnow()
                upcoming_time = now + timedelta(minutes=1)
                
                reminders = MedicationReminder.query.filter(
                    MedicationReminder.reminder_time <= upcoming_time,
                    MedicationReminder.reminder_time >= now - timedelta(minutes=1),
                    MedicationReminder.is_sent == False
                ).all()
                
                for reminder in reminders:
                    # Get medication details
                    medication = Medication.query.get(reminder.medication_id)
                    if not medication:
                        logger.error(f"Medication {reminder.medication_id} not found for reminder {reminder.id}")
                        continue
                    
                    # Send SMS
                    result = sms_service.send_reminder(
                        reminder.phone_number,
                        medication.name,
                        reminder.verification_code
                    )
                    
                    if result.get('success'):
                        # Update reminder status
                        reminder.is_sent = True
                        reminder.sent_at = datetime.utcnow()
                        # Set expiration time (next reminder or 24 hours)
                        next_reminder = MedicationReminder.query.filter(
                            MedicationReminder.medication_id == reminder.medication_id,
                            MedicationReminder.reminder_time > reminder.reminder_time
                        ).order_by(MedicationReminder.reminder_time).first()
                        
                        if next_reminder:
                            reminder.expires_at = next_reminder.reminder_time
                        else:
                            reminder.expires_at = datetime.utcnow() + timedelta(hours=24)
                        
                        db.session.commit()
                        logger.info(f"Sent reminder for medication {medication.name} to {reminder.phone_number}")
                    else:
                        logger.error(f"Failed to send reminder: {result.get('error')}")
                
                logger.info(f"Processed {len(reminders)} reminders")
            except Exception as e:
                logger.exception(f"Error processing reminders: {str(e)}")
    
    def process_expired_reminders(self):
        """Mark expired reminders as missed."""
        with self.app.app_context():
            try:
                logger.info("Processing expired reminders")
                result = mark_missed_medications()
                if 'error' in result:
                    logger.error(f"Failed to mark missed medications: {result['error']}")
                else:
                    logger.info(result['message'])
            except Exception as e:
                logger.exception(f"Error processing expired reminders: {str(e)}")

# Create a singleton scheduler instance
reminder_scheduler = ReminderScheduler() 