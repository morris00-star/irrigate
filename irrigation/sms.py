import requests
from urllib.parse import quote
import os
from django.conf import settings


def send_irrigation_alert(user, sensor_data):
    """
    Send immediate irrigation status via EgoSMS
    Returns True if SMS was sent successfully
    """
    if not user.phone_number:
        return False

    # Determine irrigation status
    status = "ACTIVE" if sensor_data.moisture < sensor_data.threshold else "IDLE"

    # Compose the message
    message = (
        f"🌱 Irrigation {status}\n"
        f"💧 Moisture: {sensor_data.moisture}%\n"
        f"📊 Threshold: {sensor_data.threshold}%\n"
        f"💦 Humidity: {sensor_data.humidity}%\n"
        f"🔧 Pump: {'ON' if sensor_data.pump_status else 'OFF'}\n"
        f"🚪 Valve: {'OPEN' if sensor_data.valve_status else 'CLOSED'}"
    )

    # Prepare EgoSMS API request
    params = {
        'username': os.getenv('EGOSMS_USERNAME'),
        'password': os.getenv('EGOSMS_PASSWORD'),
        'number': user.phone_number.lstrip('+'),
        'message': quote(message),
        'sender': quote(os.getenv('EGOSMS_SENDER_ID', 'IRRIGATE')),
        'priority': 0
    }

    try:
        response = requests.get(
            os.getenv('EGOSMS_API_URL', 'https://www.egosms.co/api/v1/plain/'),
            params=params,
            timeout=5  # 5-second timeout
        )
        return response.text.strip() == "Ok"
    except Exception as e:
        print(f"SMS failed: {str(e)}")
        return False
