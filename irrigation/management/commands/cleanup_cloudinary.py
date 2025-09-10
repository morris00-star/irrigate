from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from django.conf import settings


class Command(BaseCommand):
    help = 'Clean up corrupted files in Cloudinary'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        try:
            from cloudinary import uploader, api

            users = CustomUser.objects.exclude(profile_picture='')

            for user in users:
                if user.profile_picture:
                    filename = user.profile_picture.name

                    # Check for double extensions
                    if self.has_double_extension(filename):
                        self.stdout.write(f'Cleaning up corrupted file: {filename}')

                        # Extract public_id for Cloudinary
                        public_id = filename
                        if public_id.startswith('media/'):
                            public_id = public_id[6:]

                        # Remove file extension for public_id
                        if '.' in public_id:
                            public_id = public_id.rsplit('.', 1)[0]

                        # Delete the corrupted file from Cloudinary
                        try:
                            result = uploader.destroy(public_id)
                            self.stdout.write(f'Deleted from Cloudinary: {result}')
                        except Exception as e:
                            self.stdout.write(f'Error deleting from Cloudinary: {e}')

        except ImportError:
            self.stdout.write('Cloudinary not available')
