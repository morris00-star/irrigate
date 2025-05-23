from .views import check_and_execute_schedules
from celery import shared_task
from accounts.models import CustomUser
from irrigation.sms_utils import send_irrigation_status


@shared_task
def run_schedule_check():
    """Task to check and execute irrigation schedules."""
    check_and_execute_schedules()


@shared_task
def send_periodic_notifications():
    users = CustomUser.objects.exclude(phone_number='').exclude(phone_number__isnull=True)
    for user in users:
        send_irrigation_status(user)

