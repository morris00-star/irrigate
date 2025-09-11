from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Check current setup and URL generation'

    def handle(self, *args, **options):
        self.stdout.write("=== Current Setup ===")
        self.stdout.write(f'IS_PRODUCTION: {settings.IS_PRODUCTION}')
        self.stdout.write(f'DEFAULT_FILE_STORAGE setting: {getattr(settings, "DEFAULT_FILE_STORAGE", "Not set")}')
        self.stdout.write(f'Actual storage class: {default_storage.__class__}')

        self.stdout.write("\n=== Cloudinary Configuration ===")
        cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', None)
        api_key = getattr(settings, 'CLOUDINARY_API_KEY', None)
        api_secret = getattr(settings, 'CLOUDINARY_API_SECRET', None)

        self.stdout.write(f'CLOUDINARY_CLOUD_NAME: {cloud_name}')
        self.stdout.write(f'CLOUDINARY_API_KEY: {"SET" if api_key else "NOT SET"}')
        self.stdout.write(f'CLOUDINARY_API_SECRET: {"SET" if api_secret else "NOT SET"}')

        self.stdout.write("\n=== URL Generation Test ===")
        test_paths = [
            'profile_pics/test.jpg',
            'media/profile_pics/test.jpg',
        ]

        for path in test_paths:
            try:
                url = default_storage.url(path)
                self.stdout.write(f'{path} -> {url}')
            except Exception as e:
                self.stdout.write(f'{path} -> ERROR: {e}')

        self.stdout.write("\n=== Manual Cloudinary URL Test ===")
        if cloud_name:
            manual_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/profile_pics/test.jpg'
            self.stdout.write(f'Manual URL: {manual_url}')
