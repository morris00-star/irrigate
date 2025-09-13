# accounts/migrations/0003_safe_remove_sms_alert_frequency.py
from django.db import migrations

def safe_remove_field(apps, schema_editor):
    # This function will safely remove the field if it exists
    # If the field doesn't exist, it will do nothing
    try:
        # Check if the field exists in the database
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'accounts_customuser' 
                AND column_name = 'sms_alert_frequency'
            """)
            if cursor.fetchone():
                # Field exists, remove it
                schema_editor.execute(
                    "ALTER TABLE accounts_customuser DROP COLUMN sms_alert_frequency"
                )
    except:
        # If anything fails, just continue - the field might not exist
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_remove_customuser_sms_alert_frequency'),
    ]

    operations = [
        migrations.RunPython(safe_remove_field, migrations.RunPython.noop),
    ]
