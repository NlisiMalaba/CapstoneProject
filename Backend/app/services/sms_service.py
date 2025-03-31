import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class SMSService:
    """Service for sending SMS reminders using Twilio."""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Check if Twilio credentials are set
        self.client = None
        if self.account_sid and self.auth_token and self.from_phone:
            self.client = Client(self.account_sid, self.auth_token)
    
    def send_reminder(self, to_phone, medication_name, verification_code):
        """Send a medication reminder SMS with verification code."""
        if not self.client:
            return {'error': 'Twilio credentials not configured'}
        
        try:
            message = f"REMINDER: Time to take your {medication_name}. After taking, respond with verification code: {verification_code} to confirm."
            
            sms = self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=to_phone
            )
            
            return {
                'success': True,
                'message_id': sms.sid
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Create a singleton instance
sms_service = SMSService() 