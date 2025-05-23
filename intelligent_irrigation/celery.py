from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-every-120-seconds': {
        'task': 'irrigation.tasks.send_periodic_notifications',
        'schedule': 120.0,  # 2 minutes
    },
}
