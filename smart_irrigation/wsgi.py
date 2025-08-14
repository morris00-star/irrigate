import os
from django.core.wsgi import get_wsgi_application
import eventlet
eventlet.monkey_patch()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')
application = get_wsgi_application()
