import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from accounts.models import CustomUser
from smart_irrigation import settings


class Command(BaseCommand):
    help = 'Migrate local media files to Cloudinary'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        self.stdout.write('Starting media migration to Cloudinary...')

        # Migrate user profile pictures
        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for user in CustomUser.objects.exclude(profile_picture=''):
            if user.profile_picture:
                try:
                    # Check if file exists locally before trying to migrate
                    if user.profile_picture.storage.exists(user.profile_picture.name):
                        # Access the URL to trigger Cloudinary upload
                        url = user.get_profile_picture_url()
                        if url:
                            migrated_count += 1
                            self.stdout.write(f'✓ Migrated profile picture for {user.username}')
                        else:
                            skipped_count += 1
                            self.stdout.write(f'- Skipped {user.username} (no URL generated)')
                    else:
                        # File doesn't exist locally, skip migration
                        skipped_count += 1
                        self.stdout.write(f'- Skipped {user.username} (file not found: {user.profile_picture.name})')

                except Exception as e:
                    error_count += 1
                    self.stderr.write(f'✗ Error migrating {user.username}: {str(e)}')

        self.stdout.write(
            f'Migration complete: {migrated_count} migrated, '
            f'{skipped_count} skipped, {error_count} errors'
        )
