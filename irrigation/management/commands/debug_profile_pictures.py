from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Debug profile picture issues'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()

        for user in users:
            has_picture = bool(user.profile_picture)
            picture_name = user.profile_picture.name if user.profile_picture else None
            picture_exists = default_storage.exists(picture_name) if picture_name else False

            self.stdout.write(
                f"User: {user.username}, "
                f"Has Picture: {has_picture}, "
                f"Picture Name: {picture_name}, "
                f"Picture Exists: {picture_exists}"
            )
