from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from accounts.models import CustomUser
import os
from smart_irrigation import settings


class Command(BaseCommand):
    help = 'Migrate local media files to Cloudinary'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        # Migrate user profile pictures
        for user in CustomUser.objects.exclude(profile_picture=''):
            if user.profile_picture:
                try:
                    # This will automatically upload to Cloudinary when accessed
                    url = user.get_profile_picture_url()
                    self.stdout.write(f'Migrated profile picture for {user.
                                      username}: {url}')
                except Exception as e:
                    self.stderr.write(f'Error migrating {user.username}: {e}')