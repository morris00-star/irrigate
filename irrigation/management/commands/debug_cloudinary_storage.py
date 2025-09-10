from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Test Cloudinary storage configuration'

    def handle(self, *args, **options):
        self.stdout.write(f'Storage backend: {default_storage.__class__}')
        self.stdout.write(f'IS_PRODUCTION: {settings.IS_PRODUCTION}')

        # Test URL generation
        test_path = 'profile_pics/test_user.jpg'
        url = default_storage.url(test_path)
        self.stdout.write(f'URL for {test_path}: {url}')

        # Check if this is a Cloudinary URL
        if 'cloudinary.com' in url:
            self.stdout.write('✓ Cloudinary storage is working correctly')
        else:
            self.stdout.write('✗ Cloudinary storage is NOT working - using local URLs')
