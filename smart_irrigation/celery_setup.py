import eventlet
eventlet.monkey_patch()
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')

app = Celery('smart_irrigation', broker_connection_retry_on_startup=True,
             broker_pool_limit=None)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
