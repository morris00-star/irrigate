import requests
from urllib.parse import quote
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SMSServiceError(Exception):
    def __init__(self, message, phone_number=None, details=None):
        self.phone_number = phone_number
        self.details = details
        super().__init__(f"SMS Error: {message}")


class SMSService:
    @staticmethod
    def clean_phone_number(phone):
        """Clean and validate phone number"""
        if not phone:
            return None

        try:
            # Remove any non-digit characters except +
            cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')

            # Ensure it starts with country code
            if cleaned.startswith('+256'):
                return cleaned[1:]  # Remove + for EgoSMS
            elif cleaned.startswith('256'):
                return cleaned
            elif cleaned.startswith('0'):
                return '256' + cleaned[1:]  # Convert 07... to 2567...
            else:
                return None

        except Exception:
            return None

    @classmethod
    def send_alert(cls, user, sensor_data):
        """Send irrigation alert"""
        if not user or not user.phone_number:
            return False, "Invalid user or missing phone number"

        # Double-check that user wants notifications
        if not user.receive_sms_alerts:
            return False, "User has disabled SMS notifications"

        try:
            # Build message
            message = cls._build_alert_message(sensor_data, user)

            success, result_message = cls._send_sms(user.phone_number, message)

            return success, result_message

        except Exception as e:
            logger.error(f"Error for {user.username}: {str(e)}")
            return False, "Failed to send alert"

    @classmethod
    def _build_alert_message(cls, sensor_data, user):
        """Construct the alert message with proper None handling"""
        # Get values with proper None handling
        threshold = getattr(user, 'sms_alert_threshold', None)
        if threshold is None:
            threshold = getattr(sensor_data, 'threshold', 'N/A')

        moisture = getattr(sensor_data, 'moisture', 'N/A')

        # Handle None values for comparison
        if moisture is not None and threshold is not None and isinstance(moisture, (int, float)) and isinstance(
                threshold, (int, float)):
            status = "ACTIVE" if moisture < threshold else "IDLE"
        else:
            status = "UNKNOWN"

        # Get other values with None handling
        temperature = getattr(sensor_data, 'temperature', 'N/A')
        humidity = getattr(sensor_data, 'humidity', 'N/A')
        pump_status = getattr(sensor_data, 'pump_status', False)
        valve_status = getattr(sensor_data, 'valve_status', False)
        timestamp = getattr(sensor_data, 'timestamp')
        user = getattr(sensor_data, 'user')

        return (
            f"Hello, {user}\n!, Your farm's update;"
            f"At Time:  {timestamp}\n"
            f"Irrigation:  {status}\n"
            f"Moisture: {moisture if moisture is not None else 'N/A'}%\n"
            f"Threshold: {threshold if threshold is not None else 'N/A'}%\n"
            f"Temp: {temperature if temperature is not None else 'N/A'}°C\n"
            f"humidity: {humidity if humidity is not None else 'N/A'}%\n"
            f"Pump: {'ON' if pump_status else 'OFF'}\n"
            f"Valve: {'OPEN' if valve_status else 'CLOSED'}"
        )

    @classmethod
    def _send_sms(cls, phone, message):
        """Core SMS sending logic"""
        if settings.EGOSMS_CONFIG.get('TEST_MODE', True):
            logger.info(f"TEST MODE: SMS to {phone}: {message[:50]}...")
            return True, "Test mode - no SMS sent"

        clean_num = cls.clean_phone_number(phone)
        if not clean_num:
            return False, "Invalid phone number format"

        try:
            params = {
                'username': settings.EGOSMS_CONFIG['USERNAME'],
                'password': settings.EGOSMS_CONFIG['PASSWORD'],
                'number': clean_num,
                'message': quote(message),
                'sender': settings.EGOSMS_CONFIG['SENDER_ID'],
                'priority': 0
            }

            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{settings.EGOSMS_CONFIG['API_URL']}?{query_string}"

            response = requests.get(url, timeout=15)

            if response.text.strip() == "Ok":
                logger.info(f"SMS successfully sent to {phone}")
                return True, "SMS sent successfully"
            else:
                return False, f"EgoSMS error: {response.text}"

        except Exception as e:
            return False, f"Network error: {str(e)}"

    @classmethod
    def check_balance(cls):
        """Check EgoSMS account balance"""
        if settings.EGOSMS_CONFIG.get('TEST_MODE', True):
            return True, "Test mode - balance check skipped"

        try:
            params = {
                'username': settings.EGOSMS_CONFIG['USERNAME'],
                'password': settings.EGOSMS_CONFIG['PASSWORD'],
                'action': 'balance'
            }

            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{settings.EGOSMS_CONFIG['API_URL']}?{query_string}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                balance_text = response.text.strip()
                return True, f"Balance: {balance_text} credits"
            else:
                return False, f"HTTP error: {response.status_code}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    @classmethod
    def send_direct_sms(cls, phone_number, message):
        """Direct SMS sending"""
        if settings.EGOSMS_CONFIG.get('TEST_MODE', True):
            logger.info(f"TEST MODE: Direct SMS to {phone_number}: {message[:50]}...")
            return True, "Test mode - no SMS sent"

        clean_num = cls.clean_phone_number(phone_number)
        if not clean_num:
            return False, "Invalid phone number format"

        try:
            params = {
                'username': settings.EGOSMS_CONFIG['USERNAME'],
                'password': settings.EGOSMS_CONFIG['PASSWORD'],
                'number': clean_num,
                'message': quote(message),
                'sender': settings.EGOSMS_CONFIG['SENDER_ID'],
                'priority': 0
            }

            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{settings.EGOSMS_CONFIG['API_URL']}?{query_string}"

            response = requests.get(url, timeout=15)

            if response.text.strip() == "Ok":
                logger.info(f"Direct SMS successfully sent to {phone_number}")
                return True, "SMS sent successfully"
            else:
                return False, f"EgoSMS error: {response.text}"

        except Exception as e:
            return False, f"Network error: {str(e)}"


# Required function for compatibility
def send_irrigation_alert(user, sensor_data):
    """Legacy interface maintained for compatibility"""
    return SMSService.send_alert(user, sensor_data)
