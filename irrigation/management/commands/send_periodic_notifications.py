from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from irrigation.models import SensorData
from irrigation.sms import SMSService
import logging
from time import sleep
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sends periodic irrigation alerts via SMS with comprehensive error handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Polling interval in seconds (default: 300)'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Max retries for failed SMS (default: 3)'
        )

    def handle(self, *args, **options):
        retry_count = 0
        max_retries = options['max_retries']

        while True:
            try:
                self._send_notifications()
                retry_count = 0  # Reset on success
                sleep(options['interval'])

            except ObjectDoesNotExist:
                logger.warning("No sensor data available - retrying in 60s")
                sleep(60)
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded. Exiting.")
                    break

                sleep_duration = min(300, 60 * retry_count)  # Exponential backoff
                logger.error(f"Error occurred (retry {retry_count}/{max_retries}): {str(e)}")
                sleep(sleep_duration)

    def _send_notifications(self):
        """Send notifications to all active users with phone numbers"""
        try:
            latest_data = SensorData.objects.latest('timestamp')
        except ObjectDoesNotExist:
            logger.warning("No sensor data available in database")
            raise

        users = CustomUser.objects.filter(
            is_active=True,
            phone_number__isnull=False
        ).exclude(phone_number='')

        if not users.exists():
            logger.warning("No active users with phone numbers found")
            return

        for user in users:
            success, message = SMSService.send_alert(user, latest_data)
            if success:
                logger.info(f"Successfully sent to {user.phone_number}")
            else:
                logger.error(f"Failed to send to {user.phone_number}: {message}")
