import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')

app = Celery('smart_irrigation')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Scheduled tasks
app.conf.beat_schedule = {
    'send-irrigation-alerts': {
        'task': 'irrigation.tasks.send_scheduled_alerts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

app.autodiscover_tasks()
