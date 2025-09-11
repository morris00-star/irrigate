from django.core.management.base import BaseCommand
from irrigation.url_utils import get_media_url


class Command(BaseCommand):
    help = 'Test the URL utility function'

    def handle(self, *args, **options):
        self.stdout.write("Testing URL utility function")

        # Create a proper mock file field
        class MockFile:
            def __init__(self, name, url):
                self.name = name
                self._url = url

            @property
            def url(self):
                return self._url

        # Test cases
        test_cases = [
            # (file_name, storage_url, expected_result_pattern)
            ('profile_pics/test.jpg', '/media/profile_pics/test.jpg', '/media/'),
            ('media/profile_pics/test.jpg', '/media/profile_pics/test.jpg', '/media/'),
            (None, None, None),  # No file
        ]

        for file_name, storage_url, expected_pattern in test_cases:
            mock_file = MockFile(file_name, storage_url) if file_name else None
            result = get_media_url(mock_file)

            self.stdout.write(f"\nInput: {file_name}, {storage_url}")
            self.stdout.write(f"Output: {result}")

            if expected_pattern and result and expected_pattern in result:
                self.stdout.write("✓ PASS")
            elif not expected_pattern and not result:
                self.stdout.write("✓ PASS (None expected)")
            else:
                self.stdout.write("✗ FAIL")
