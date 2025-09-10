from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Debug Cloudinary storage configuration'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        try:
            # Test the storage backend
            self.stdout.write(f'Default storage: {default_storage}')
            self.stdout.write(f'Storage class: {default_storage.__class__}')

            # Test URL generation
            test_path = 'profile_pics/test_user.jpg'
            url = default_storage.url(test_path)
            self.stdout.write(f'Generated URL for {test_path}: {url}')

            # Check if Cloudinary storage is being used
            if hasattr(default_storage, 'cloudinary'):
                self.stdout.write('Cloudinary storage is active')
                self.stdout.write(f'Cloudinary config: {default_storage.cloudinary.config}')
            else:
                self.stdout.write('Cloudinary storage is NOT active')

        except Exception as e:
            self.stderr.write(f'Debug failed: {str(e)}')
            import traceback
            traceback.print_exc()
