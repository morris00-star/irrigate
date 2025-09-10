from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Test Cloudinary file upload'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        try:
            from cloudinary import uploader

            # Test upload a simple image
            test_image = ContentFile(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x00\x00\x00\x00IEND\xaeB`\x82',
                name='test.png'
            )

            # Upload to Cloudinary
            result = uploader.upload(
                test_image,
                folder='profile_pics',
                public_id='test_user',
                overwrite=True
            )

            self.stdout.write(f'Cloudinary upload result: {result["url"]}')
            self.stdout.write(f'Public ID: {result["public_id"]}')
            self.stdout.write(f'Format: {result["format"]}')
            self.stdout.write(f'Version: {result["version"]}')

            # Test generating URL
            from cloudinary import CloudinaryImage
            img = CloudinaryImage(result["public_id"])
            url = img.build_url()
            self.stdout.write(f'Generated URL: {url}')

        except Exception as e:
            self.stderr.write(f'Cloudinary test failed: {str(e)}')
            import traceback
            traceback.print_exc()
