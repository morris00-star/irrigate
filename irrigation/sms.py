import requests
from urllib.parse import quote
from django.conf import settings
from django.utils import timezone
import logging
import re
from typing import Optional, Tuple, Dict
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class SMSServiceError(Exception):
    """Enhanced exception for SMS failures"""

    def __init__(self, message: str, phone_number: str = None, details: str = None):
        self.phone_number = phone_number
        self.details = details
        super().__init__(f"SMS Error: {message}")


class SMSService:
    @staticmethod
    def clean_ugandan_number(phone: str) -> Optional[str]:
        """Strict validation for Ugandan numbers with improved regex"""
        if not phone:
            return None

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Validate formats: +256..., 256..., 07..., 7...
        if re.match(r'^\+?256\d{9}$', cleaned):
            return cleaned.lstrip('+')
        if re.match(r'^0?[7|7]\d{8}$', cleaned):  # Accepts 07... or 7...
            return '256' + cleaned[-9:]
        return None

    @classmethod
    def validate_sensor_data(cls, sensor_data) -> bool:
        """Validate sensor data before sending"""
        if not sensor_data:
            raise SMSServiceError("No sensor data provided")

        required_fields = ['moisture', 'threshold', 'temperature',
                           'pump_status', 'valve_status', 'timestamp']
        for field in required_fields:
            if not hasattr(sensor_data, field):
                raise SMSServiceError(f"Missing sensor data field: {field}")
        return True

    @classmethod
    def send_alert(cls, user, sensor_data) -> Tuple[bool, str]:
        """Send irrigation alert with comprehensive error handling"""
        if not user or not user.phone_number:
            return False, "Invalid user or missing phone number"

        try:
            cls.validate_sensor_data(sensor_data)

            alert_time = timezone.localtime(sensor_data.timestamp).strftime("%Y-%m-%d %H:%M:%S")

            message = cls._build_alert_message(sensor_data, alert_time)
            return cls._send_sms(user.phone_number, message)

        except SMSServiceError as e:
            logger.error(f"Validation failed for {user.username}: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error for {user.username}: {str(e)}")
            return False, "Failed to send alert"

    @classmethod
    def _build_alert_message(cls, sensor_data, alert_time: str) -> str:
        """Construct the alert message with emojis"""
        return (
            u"🕒 {time}\n"
            u"🌱 Status: {status}\n"
            u"💧 Moisture: {moisture}%\n"
            u"📊 Threshold: {threshold}%\n"
            u"🌡️ Temp: {temp}°C\n"
            u"🔧 Pump: {pump}\n"
            u"🚪 Valve: {valve}"
        ).format(
            time=alert_time,
            status="ACTIVE" if sensor_data.moisture < sensor_data.threshold else "IDLE",
            moisture=getattr(sensor_data, 'moisture', 'N/A'),
            threshold=getattr(sensor_data, 'threshold', 'N/A'),
            temp=getattr(sensor_data, 'temperature', 'N/A'),
            pump="ON" if getattr(sensor_data, 'pump_status', False) else "OFF",
            valve="OPEN" if getattr(sensor_data, 'valve_status', False) else "CLOSED"
        )

    @classmethod
    def _send_sms(cls, phone: str, message: str) -> Tuple[bool, str]:
        """Core SMS sending logic with improved error handling"""
        if settings.EGOSMS_CONFIG.get('TEST_MODE', True):
            logger.info(f"TEST MODE: SMS to {phone}: {message[:50]}...")
            return True, "Test mode - no SMS sent"

        clean_num = cls.clean_ugandan_number(phone)
        if not clean_num:
            return False, "Invalid phone number format"

        try:
            response = cls._make_egosms_request(clean_num, message)
            return cls._handle_egosms_response(response, phone)

        except RequestException as e:
            raise SMSServiceError("Network error", phone, str(e))
        except Exception as e:
            raise SMSServiceError("SMS sending failed", phone, str(e))

    @classmethod
    def _make_egosms_request(cls, number: str, message: str) -> requests.Response:
        """Make the actual API request to EgoSMS"""
        params = {
            'username': settings.EGOSMS_CONFIG['USERNAME'],
            'password': settings.EGOSMS_CONFIG['PASSWORD'],
            'number': number,
            'message': quote(message),
            'sender': settings.EGOSMS_CONFIG['SENDER_ID'],
            'priority': 0
        }
        return requests.get(
            settings.EGOSMS_CONFIG['API_URL'],
            params=params,
            timeout=15  # Increased timeout
        )

    @classmethod
    def _handle_egosms_response(cls, response: requests.Response, phone: str) -> Tuple[bool, str]:
        """Process the response from EgoSMS"""
        if response.status_code != 200:
            raise SMSServiceError(f"HTTP {response.status_code}", phone)

        response_text = response.text.strip()

        if response_text == "Ok":
            return True, "SMS sent successfully"

        error_map = {
            "100": "Invalid credentials",
            "101": "Insufficient balance",
            "102": "Invalid sender ID",
            "103": "Invalid phone number",
            "104": "Message too long",
            "105": "Invalid priority",
            "106": "Service unavailable"
        }

        error_msg = error_map.get(response_text, f"Unknown error: {response_text}")
        raise SMSServiceError(error_msg, phone)


# Legacy interface
send_irrigation_alert = SMSService.send_alert
