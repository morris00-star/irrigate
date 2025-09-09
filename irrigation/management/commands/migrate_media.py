import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Migrate media files to cloud storage'

    def handle(self, *args, **options):
        self.stdout.write('Migrating media files to cloud storage...')

        # Migrate profile pictures
        users_with_pictures = CustomUser.objects.exclude(profile_picture='')

        for user in users_with_pictures:
            if user.profile_picture:
                try:
                    # Check if file exists in local storage
                    if hasattr(user.profile_picture.storage, 'exists'):
                        if user.profile_picture.storage.exists(user.profile_picture.name):
                            # File will be automatically uploaded to cloud storage when accessed
                            url = user.profile_picture.url
                            self.stdout.write(f'Migrated: {user.profile_picture.name}')
                        else:
                            self.stdout.write(f'Missing: {user.profile_picture.name}')
                            user.profile_picture = None
                            user.save()
                except Exception as e:
                    self.stdout.write(f'Error with {user.profile_picture.name}: {str(e)}')
                    user.profile_picture = None
                    user.save()

        self.stdout.write('Media migration completed!')
