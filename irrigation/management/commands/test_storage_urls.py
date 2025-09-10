from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Test storage URL generation'

    def handle(self, *args, **options):
        # Test various file paths
        test_paths = [
            'profile_pics/user_2.jpg',
            'profile_pics/user_2.png',
            'media/profile_pics/user_2.jpg',
            'profile_pics/user_2',  # Without extension
        ]

        for path in test_paths:
            try:
                url = default_storage.url(path)
                self.stdout.write(f'{path} -> {url}')
            except Exception as e:
                self.stderr.write(f'Error with {path}: {str(e)}')
