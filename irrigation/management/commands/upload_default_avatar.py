from django.core.management.base import BaseCommand
import os
from pathlib import Path
from smart_irrigation import settings


class Command(BaseCommand):
    help = 'Create and upload default avatar to Cloudinary'

    def handle(self, *args, **options):
        if not settings.IS_PRODUCTION:
            self.stdout.write('This command is only for production use')
            return

        try:
            # Create a simple default avatar using Pillow
            try:
                from PIL import Image, ImageDraw

                # Create a 150x150 image with light gray background
                img = Image.new('RGB', (150, 150), color='#cccccc')
                draw = ImageDraw.Draw(img)

                # Draw a simple person icon
                draw.ellipse((25, 25, 125, 125), outline='#999999', width=5)

                # Save to a temporary file
                temp_path = '/tmp/default_avatar.png'
                img.save(temp_path)

                # Upload to Cloudinary
                from cloudinary import uploader
                with open(temp_path, 'rb') as f:
                    result = uploader.upload(
                        f,
                        public_id="default_avatar",
                        folder="media"
                    )

                self.stdout.write(f'Default avatar uploaded to: {result["secure_url"]}')

                # Clean up
                os.remove(temp_path)

            except ImportError:
                # Pillow not available, create a simple SVG instead
                svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150">
                    <circle cx="75" cy="60" r="30" fill="#cccccc" stroke="#999999" stroke-width="3"/>
                    <circle cx="75" cy="150" r="50" fill="#cccccc" stroke="#999999" stroke-width="3"/>
                </svg>'''

                # Upload SVG to Cloudinary
                from cloudinary import uploader
                result = uploader.upload(
                    svg_content,
                    public_id="default_avatar",
                    folder="media",
                    resource_type="raw"  # Important for SVG files
                )

                self.stdout.write(f'Default SVG avatar uploaded to: {result["secure_url"]}')

        except Exception as e:
            self.stderr.write(f'Error uploading default avatar: {str(e)}')
            # Create a fallback local default avatar
            self.create_local_default_avatar()

    def create_local_default_avatar(self):
        """Create a local default avatar as fallback"""
        try:
            local_avatar_path = os.path.join(settings.BASE_DIR, 'accounts', 'static', 'default_avatar.svg')
            os.makedirs(os.path.dirname(local_avatar_path), exist_ok=True)

            svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150">
                <circle cx="75" cy="60" r="30" fill="#cccccc" stroke="#999999" stroke-width="3"/>
                <circle cx="75" cy="150" r="50" fill="#cccccc" stroke="#999999" stroke-width="3"/>
            </svg>'''

            with open(local_avatar_path, 'w') as f:
                f.write(svg_content)

            self.stdout.write(f'Local default avatar created at: {local_avatar_path}')

        except Exception as e:
            self.stderr.write(f'Error creating local default avatar: {str(e)}')
