from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from irrigation.models import SensorData
from irrigation.sms import SMSService
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sends irrigation alerts via SMS'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=300, help='Polling interval in seconds')

    def handle(self, *args, **options):
        while True:
            try:
                latest_data = SensorData.objects.latest('timestamp')
                users = CustomUser.objects.filter(
                    is_active=True,
                    phone_number__isnull=False
                ).exclude(phone_number='')

                for user in users:
                    success, _ = SMSService.send_alert(user, latest_data)
                    logger.info(f"{'Success' if success else 'Failed'} sending to {user.phone_number}")

                time.sleep(options['interval'])

            except SensorData.DoesNotExist:
                logger.warning("No sensor data available")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Worker crashed: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before restarting
