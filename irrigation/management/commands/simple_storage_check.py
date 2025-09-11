from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Simple storage configuration check'

    def handle(self, *args, **options):
        self.stdout.write(f'IS_PRODUCTION: {settings.IS_PRODUCTION}')
        self.stdout.write(f'DEFAULT_FILE_STORAGE setting: {settings.DEFAULT_FILE_STORAGE}')
        self.stdout.write(f'Actual storage class: {default_storage.__class__}')

        # Test URL generation
        test_path = 'profile_pics/test.jpg'
        try:
            url = default_storage.url(test_path)
            self.stdout.write(f'URL for {test_path}: {url}')

            if 'cloudinary.com' in url:
                self.stdout.write('✓ Using Cloudinary storage')
            else:
                self.stdout.write('✗ Using local storage (not Cloudinary)')

        except Exception as e:
            self.stdout.write(f'Error generating URL: {e}')
