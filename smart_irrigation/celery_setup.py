from .eventlet_patch import *  # noqa

import os
from celery import Celery
from django.db import connections

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')

app = Celery('smart_irrigation', 
             broker_connection_retry_on_startup=True,
             broker_pool_limit=None)


# Close all DB connections before forking
@app.on_after_configure.connect
def close_db_connections(**kwargs):
    connections.close_all()


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
