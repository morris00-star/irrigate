from celery import shared_task
from .models import SensorData
from accounts.models import CustomUser
from .sms import SMSService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="irrigation.tasks.send_periodic_sms_alerts")  # Note the bind=True parameter
def send_periodic_sms_alerts(self):  # Add 'self' parameter
    """Task to send SMS alerts with proper Celery task signature"""
    try:
        latest_data = SensorData.objects.order_by('-timestamp').first()
        if not latest_data:
            logger.warning("No sensor data available")
            return "No data available"

        users = CustomUser.objects.filter(
            is_active=True,
            phone_number__isnull=False
        ).exclude(phone_number='')

        for user in users:
            SMSService.send_alert(user, latest_data)

        logger.info(f"Sent SMS alerts to {users.count()} users")
        return f"Successfully sent to {users.count()} users"

    except Exception as e:
        logger.error(f"SMS task failed: {str(e)}")
        self.retry(exc=e, countdown=60)
        return None

