import os
import phonenumbers
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import secrets
from cloudinary.models import CloudinaryField


def user_profile_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    # Generate a new filename using the user's id
    profile_picture = CloudinaryField('image', blank=True, null=True)
    filename = f'profile_pics/user_{instance.id}.{ext}'
    # If the file already exists, delete it
    if instance.profile_picture:
        old_file_path = instance.profile_picture.path
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    return filename


def validate_phone_number(value):
    try:
        phone_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError("Invalid phone number")
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError("Invalid phone number format")


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text="Format: +[country code][number], e.g., +1234567890"
    )
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
