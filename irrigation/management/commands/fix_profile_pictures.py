from django.core.management.base import BaseCommand
from accounts.models import CustomUser
import os


class Command(BaseCommand):
    help = 'Find and fix corrupted profile picture references'

    def handle(self, *args, **options):
        users = CustomUser.objects.exclude(profile_picture='')

        fixed_count = 0
        corrupted_count = 0

        for user in users:
            if user.profile_picture:
                filename = user.profile_picture.name

                # Check for double extensions
                if self.has_double_extension(filename):
                    corrupted_count += 1
                    self.stdout.write(f'Corrupted filename: {filename}')

                    # Fix the filename
                    fixed_filename = self.fix_filename(filename)
                    self.stdout.write(f'Fixed filename: {fixed_filename}')

                    # Update the user
                    user.profile_picture.name = fixed_filename
                    user.save(update_fields=['profile_picture'])
                    fixed_count += 1

                    self.stdout.write(f'Fixed user {user.username}')

        self.stdout.write(f'Fixed {fixed_count} corrupted profile pictures')
        self.stdout.write(f'Found {corrupted_count} corrupted references')


    def has_double_extension(self, filename):
        """Check if filename has double extensions like .jpg.jpg"""
        basename = os.path.basename(filename)
        name_parts = basename.split('.')

        # If there are more than 2 parts and the last part is an image extension
        if len(name_parts) > 2:
            extensions = ['jpg', 'jpeg', 'png', 'gif']
            if name_parts[-1].lower() in extensions and name_parts[-2].lower() in extensions:
                return True
        return False

    def fix_filename(self, filename):
        """Fix double extensions in filename"""
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)

        name_parts = basename.split('.')

        # Remove duplicate extensions
        if len(name_parts) > 2:
            # Keep the first part and the last extension
            fixed_basename = f"{'.'.join(name_parts[:-2])}.{name_parts[-1]}"
            return os.path.join(dirname, fixed_basename)

        return filename
