import requests
from urllib.parse import quote
import os
from django.conf import settings


def send_irrigation_alert(user, sensor_data):
    """
    Send comprehensive irrigation status via EgoSMS
    Includes: Moisture, Threshold, Humidity, Pump & Valve status
    Returns: True if SMS sent successfully
    """
    if not user.phone_number:
        return False

    # Determine irrigation status
    irrigation_status = "ACTIVE" if sensor_data.moisture < sensor_data.threshold else "IDLE"

    # Compose optimized message (under 160 chars)
    message = (
        f"🌱 Irrigation {irrigation_status}\n"
        f"💧 Moisture: {sensor_data.moisture}%\n"
        f"📊 Threshold: {sensor_data.threshold}%\n"
        f"💦 Humidity: {sensor_data.humidity}%\n"
        f"🔧 Pump: {'ON' if sensor_data.pump_status else 'OFF'}\n"
        f"🚪 Valve: {'OPEN' if sensor_data.valve_status else 'CLOSED'}\n"
        f"Next update in 5 mins"
    )

    # Prepare API request
    params = {
        'username': os.getenv('EGOSMS_USERNAME'),
        'password': os.getenv('EGOSMS_PASSWORD'),
        'number': user.phone_number.lstrip('+'),  # Remove '+' prefix
        'message': quote(message),
        'sender': quote(os.getenv('EGOSMS_SENDER_ID')),
        'priority': 0  # Highest priority
    }

    try:
        response = requests.get(os.getenv('EGOSMS_API_URL'), params=params)
        return response.text.strip() == "Ok"
    except Exception as e:
        print(f"SMS sending failed: {str(e)}")
        return False
