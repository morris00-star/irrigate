import requests
from urllib.parse import quote
from django.conf import settings
from django.utils import timezone
import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SMSServiceError(Exception):
    """Enhanced exception for SMS failures"""

    def __init__(self, message, phone_number=None):
        self.phone_number = phone_number
        super().__init__(f"{message} (phone: {phone_number})")


class SMSService:
    @staticmethod
    def clean_ugandan_number(phone: str) -> Optional[str]:
        """Strict validation for Ugandan numbers"""
        if not phone:
            return None

        # Standardize formats: +256..., 256..., 07..., 7...
        cleaned = re.sub(r'[^\d+]', '', phone)
        if re.match(r'^\+?256\d{9}$', cleaned):
            return cleaned.lstrip('+')
        if re.match(r'^0?\d{9}$', cleaned):
            return '256' + cleaned[-9:]
        return None

    @classmethod
    def send_alert(cls, user, sensor_data) -> Tuple[bool, str]:
        """Send irrigation alert using sensor data timestamp"""
        if not user.phone_number:
            return False, "No phone number"

        try:
            # Use sensor's timestamp instead of current time
            alert_time = timezone.localtime(sensor_data.timestamp).strftime("%Y-%m-%d %H:%M:%S")

            message = (
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
                moisture=sensor_data.moisture,
                threshold=sensor_data.threshold,
                temp=sensor_data.temperature,
                pump="ON" if sensor_data.pump_status else "OFF",
                valve="OPEN" if sensor_data.valve_status else "CLOSED"
            )

            return cls._send_sms(user.phone_number, message)

        except Exception as e:
            logger.error(f"Alert failed for {user.username}: {str(e)}")
            return False, str(e)

    @classmethod
    def _send_sms(cls, phone: str, message: str) -> Tuple[bool, str]:
        """Core SMS sending logic"""
        if settings.EGOSMS_CONFIG.get('TEST_MODE'):
            logger.info(f"TEST SMS to {phone}: {message[:50]}...")
            return True, "Test mode"

        clean_num = cls.clean_ugandan_number(phone)
        if not clean_num:
            return False, "Invalid number format"

        try:
            response = requests.get(
                settings.EGOSMS_CONFIG['API_URL'],
                params={
                    'username': settings.EGOSMS_CONFIG['USERNAME'],
                    'password': settings.EGOSMS_CONFIG['PASSWORD'],
                    'number': clean_num,
                    'message': quote(message),
                    'sender': settings.EGOSMS_CONFIG['SENDER_ID'],
                    'priority': 0
                },
                timeout=10
            )
            return (response.text.strip() == "Ok", response.text)
        except Exception as e:
            raise SMSServiceError(f"SMS failed: {str(e)}", phone)


# Legacy interface
send_irrigation_alert = SMSService.send_alert