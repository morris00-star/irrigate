from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Clean up broken media file references'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up broken media references...')

        cleaned_count = 0

        for user in CustomUser.objects.exclude(profile_picture=''):
            if user.profile_picture:
                try:
                    # Check if file exists
                    if not default_storage.exists(user.profile_picture.name):
                        # File doesn't exist, clear the reference
                        user.profile_picture = None
                        user.save(update_fields=['profile_picture'])
                        cleaned_count += 1
                        self.stdout.write(f'Cleaned profile picture reference for {user.username}')

                except Exception as e:
                    self.stderr.write(f'Error processing {user.username}: {str(e)}')

        self.stdout.write(f'Cleaned {cleaned_count} broken media references')
