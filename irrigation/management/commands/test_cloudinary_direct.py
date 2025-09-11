from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test Cloudinary directly'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This test is for production only')
            return

        try:
            from cloudinary import uploader, api

            # Test Cloudinary connection
            result = api.ping()
            self.stdout.write(f'Cloudinary ping: {result}')

            # Test upload
            test_result = uploader.upload(
                'https://res.cloudinary.com/demo/image/upload/sample.jpg',
                public_id='test_upload'
            )
            self.stdout.write(f'Cloudinary upload: {test_result["url"]}')

            # Test URL generation
            from cloudinary import CloudinaryImage
            img = CloudinaryImage('test_upload')
            url = img.build_url()
            self.stdout.write(f'Cloudinary URL: {url}')

        except Exception as e:
            self.stderr.write(f'Cloudinary test failed: {str(e)}')
            import traceback
            traceback.print_exc()
