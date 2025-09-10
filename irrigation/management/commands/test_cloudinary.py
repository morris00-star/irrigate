from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Cloudinary connection'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        try:
            from cloudinary import api
            # Test Cloudinary connection
            result = api.ping()
            self.stdout.write(f'Cloudinary ping result: {result}')

            # Test upload
            from cloudinary import uploader
            test_result = uploader.upload(
                'https://res.cloudinary.com/demo/image/upload/sample.jpg',
                public_id='test_upload'
            )
            self.stdout.write(f'Cloudinary test upload: {test_result["url"]}')

        except Exception as e:
            self.stderr.write(f'Cloudinary test failed: {str(e)}')
