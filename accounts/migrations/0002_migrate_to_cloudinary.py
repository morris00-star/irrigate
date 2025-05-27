from django.db import migrations
from cloudinary.uploader import upload
import os


def migrate_to_cloudinary(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    for user in CustomUser.objects.exclude(profile_picture=''):
        if user.profile_picture and hasattr(user.profile_picture, 'path'):
            if os.path.exists(user.profile_picture.path):
                try:
                    result = upload(
                        user.profile_picture.path,
                        folder="profile_pics",
                        public_id=f"user_{user.id}",
                        overwrite=True
                    )
                    user.profile_picture = result['public_id']
                    user.save()
                    # Remove the local file after successful upload
                    os.remove(user.profile_picture.path)
                except Exception as e:
                    print(f"Failed to migrate user {user.id}: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '00XX_previous_migration'),  # Replace XX with your last migration number
    ]

    operations = [
        migrations.RunPython(migrate_to_cloudinary),
    ]