from celery import shared_task
from django.contrib.auth import get_user_model
from irrigation.models import SensorData
from irrigation.sms import send_irrigation_alert
from django.utils import timezone

User = get_user_model()


@shared_task
def send_scheduled_alerts():
    """Send irrigation status alerts every 5 minutes"""
    # Get users with recent sensor data (last 10 mins)
    time_threshold = timezone.now() - timezone.timedelta(minutes=10)

    active_users = User.objects.filter(
        sensordata__timestamp__gte=time_threshold
    ).distinct()

    for user in active_users:
        latest_data = SensorData.objects.filter(
            user=user
        ).order_by('-timestamp').first()

        if latest_data:
            send_irrigation_alert(user, latest_data)
            