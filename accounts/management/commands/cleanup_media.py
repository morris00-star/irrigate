from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Clean up references to missing media files'

    def handle(self, *args, **options):
        users = CustomUser.objects.exclude(profile_picture='')

        for user in users:
            if user.profile_picture:
                try:
                    # Try to access the URL - will fail if file doesn't exist
                    user.profile_picture.url
                    self.stdout.write(f'✓ OK: {user.profile_picture.name}')
                except Exception as e:
                    self.stdout.write(f'✗ Missing: {user.profile_picture.name} - {e}')
                    user.profile_picture = None
                    user.save()
                    self.stdout.write(f'  → Cleaned up reference')

        self.stdout.write('Media cleanup completed!')
