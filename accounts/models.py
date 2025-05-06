import os
from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets


def user_profile_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    # Generate a new filename using the user's id
    filename = f'profile_pics/user_{instance.id}.{ext}'
    # If the file already exists, delete it
    if instance.profile_picture:
        old_file_path = instance.profile_picture.path
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    return filename


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the profile picture file when the user is deleted
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)
