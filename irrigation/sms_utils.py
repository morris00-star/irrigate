from django.conf import settings
from twilio.rest import Client
from accounts.models import CustomUser
from irrigation.models import SensorData
from django.utils import timezone
from datetime import timedelta


def send_irrigation_status(user):
    """
    Send current irrigation status via SMS (cross-app import)
    """
    if not user.phone_number:
        return False

    try:
        # Get the latest sensor data (within last 2 minutes)
        two_minutes_ago = timezone.now() - timedelta(minutes=2)
        sensor_data = SensorData.objects.filter(
            user=user,
            timestamp__gte=two_minutes_ago
        ).order_by('-timestamp').first()

        if not sensor_data:
            return False

        # Format the message
        message_body = (
            f"Hello {user.first_name or 'User'},\n\n"
            f"Current Irrigation Status (2-min update):\n"
            f"Moisture: {sensor_data.moisture}%\n"
            f"Threshold: {sensor_data.threshold}%\n"
            f"Temperature: {sensor_data.temperature}°C\n"
            f"Humidity: {sensor_data.humidity}%\n"
            f"Pump: {'ON' if sensor_data.pump_status else 'OFF'}\n"
            f"Valve: {'OPEN' if sensor_data.valve_status else 'CLOSED'}\n\n"
            f"System is {'active' if sensor_data.pump_status else 'inactive'}."
        )

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        return True

    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return False
