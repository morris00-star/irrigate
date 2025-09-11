from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Test Cloudinary configuration'

    def handle(self, *args, **options):
        self.stdout.write(f'IS_PRODUCTION: {settings.IS_PRODUCTION}')
        self.stdout.write(f'DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}')
        self.stdout.write(f'Storage class: {default_storage.__class__}')
        self.stdout.write(f'Storage module: {default_storage.__class__.__module__}')

        # Test URL generation
        test_path = 'profile_pics/test.jpg'
        url = default_storage.url(test_path)
        self.stdout.write(f'URL for {test_path}: {url}')

        # Check if this is a Cloudinary URL
        if 'cloudinary.com' in url:
            self.stdout.write('✓ Cloudinary URL generation working')
        else:
            self.stdout.write('✗ Cloudinary URL generation NOT working')

        # Test if we can actually use the storage
        try:
            # Test if storage is working
            exists = default_storage.exists(test_path)
            self.stdout.write(f'File exists check: {exists}')
        except Exception as e:
            self.stdout.write(f'Storage test failed: {e}')
