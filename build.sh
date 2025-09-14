#!/usr/bin/env bash
# build.sh

set -o errexit

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_remote.txt

# Create necessary directories
mkdir -p media/profile_pics
mkdir -p accounts/static/

# Collect static files
python manage.py collectstatic --noinput

# First, ensure the database has all required columns
echo "Ensuring database schema matches model..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_irrigation.settings')
django.setup()

from django.db import connection

# Add missing columns without failing if they already exist
sql_commands = [
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS sms_alert_threshold INTEGER DEFAULT 30',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS sms_notification_frequency INTEGER DEFAULT 15',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS receive_sms_alerts BOOLEAN DEFAULT false',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS last_notification_sent TIMESTAMP WITH TIME ZONE NULL',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS quiet_hours_start TIME DEFAULT \\'22:00:00\\'',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS quiet_hours_end TIME DEFAULT \\'06:00:00\\'',
    'ALTER TABLE accounts_customuser ADD COLUMN IF NOT EXISTS last_sms_alert TIMESTAMP WITH TIME ZONE NULL',
]

try:
    with connection.cursor() as cursor:
        for sql in sql_commands:
            try:
                cursor.execute(sql)
                print(f'Executed: {sql}')
            except Exception as e:
                print(f'Note: {e}')
except Exception as e:
    print(f'Database setup completed with notes: {e}')
"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate

echo "Build completed successfully!"
