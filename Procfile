web: gunicorn smart_irrigation.wsgi:application
worker: celery -A intelligent_irrigation worker -Q sms --loglevel=info
beat: celery -A intelligent_irrigation beat --loglevel=info
