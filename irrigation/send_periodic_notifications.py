from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from irrigation.sms_utils import send_irrigation_status
import time


class Command(BaseCommand):
    help = 'Test notification system'

    def handle(self, *args, **options):
        while True:
            users = CustomUser.objects.exclude(phone_number='').exclude(phone_number__isnull=True)
            for user in users:
                if send_irrigation_status(user):
                    self.stdout.write(f"Sent to {user.username}")
                else:
                    self.stdout.write(f"Failed for {user.username}")
            time.sleep(120)  # 2 minutes
