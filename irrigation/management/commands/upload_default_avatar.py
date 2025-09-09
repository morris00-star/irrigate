from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import requests
from io import BytesIO
from smart_irrigation import settings


class Command(BaseCommand):
    help = 'Upload default avatar to Cloudinary'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        # Download a simple default avatar
        default_avatar_url = "https://via.placeholder.com/150/cccccc/999999?text=Avatar"

        try:
            response = requests.get(default_avatar_url)
            if response.status_code == 200:
                # Upload to Cloudinary
                from cloudinary import uploader
                result = uploader.upload(
                    BytesIO(response.content),
                    public_id="default_avatar",
                    folder="media"
                )
                self.stdout.write(f'Default avatar uploaded to: {result["url"]}')
            else:
                self.stderr.write('Failed to download default avatar')

        except Exception as e:
            self.stderr.write(f'Error uploading default avatar: {str(e)}')
