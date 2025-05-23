import os
import time
from django.core.management import call_command

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligent_irrigation.settings')

    while True:
        print("Sending notifications...")
        call_command('send_periodic_notifications')
        time.sleep(120)  # 2 minutes
