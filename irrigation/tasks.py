from celery import shared_task
from .views import check_and_execute_schedules


@shared_task
def run_schedule_check():
    """Task to check and execute irrigation schedules."""
    check_and_execute_schedules()
