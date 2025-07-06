
web: gunicorn smart_irrigation.wsgi:application
worker: celery -A irrigation_system worker --loglevel=info
beat: celery -A irrigation_system beat --loglevel=info
