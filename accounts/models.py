import os
import phonenumbers
from django.core.files.storage import default_storage
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from smart_irrigation import settings
from .utils import get_cloudinary_url


def user_profile_path(instance, filename):
    """Generate path for user profile pictures"""
    ext = filename.split('.')[-1]
    filename = f'profile_pics/user_{instance.id}.{ext}'

    # Only try to delete old file if it exists locally (development)
    if instance.profile_picture and not settings.IS_PRODUCTION:
        try:
            old_file_path = instance.profile_picture.path
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        except (ValueError, AttributeError, OSError):
            # Ignore errors - file might be in Cloudinary or doesn't exist
            pass

    return filename


def validate_phone_number(value):
    try:
        phone_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError("Invalid phone number: start with +[country code][number]")
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError("Invalid phone number: start with +[country code][number]")


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text="Format: +[country code][number]"
    )
    receive_sms_alerts = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        # Check if this is a new user
        is_new_user = self.pk is None

        # Store the old profile picture if user exists
        old_profile_picture = None
        if not is_new_user:
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                old_profile_picture = old_user.profile_picture
            except CustomUser.DoesNotExist:
                pass

        # Check if profile picture field is set but file doesn't exist (development only)
        if (self.profile_picture and
                hasattr(self.profile_picture, 'name') and
                not settings.IS_PRODUCTION and  # Only check in development
                not default_storage.exists(self.profile_picture.name)):
            # Clear the reference if file doesn't exist
            print(f"DEBUG: Clearing missing profile picture in development: {self.profile_picture.name}")
            self.profile_picture = None

        # Call the parent save method
        super().save(*args, **kwargs)

        # Create a token for the user when they're created
        if is_new_user and not hasattr(self, 'auth_token'):
            Token.objects.create(user=self)

        # Handle old file deletion for local development only
        if (not is_new_user and old_profile_picture and
                self.profile_picture != old_profile_picture and
                not settings.IS_PRODUCTION):  # Only in development
            self._delete_old_profile_picture(old_profile_picture)


    def _delete_old_profile_picture(self, old_picture):
        """Safely delete old profile picture"""
        try:
            # Local development - delete file from filesystem
            if old_picture and os.path.isfile(old_picture.path):
                os.remove(old_picture.path)
        except (ValueError, AttributeError, OSError):
            # Ignore errors during file deletion
            pass

    def delete(self, *args, **kwargs):
        # Only try to delete local files in development
        if not settings.IS_PRODUCTION and self.profile_picture:
            try:
                if os.path.isfile(self.profile_picture.path):
                    os.remove(self.profile_picture.path)
            except (ValueError, AttributeError, OSError):
                # Ignore errors during file deletion
                pass
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('profile')


    def get_profile_picture_url(self):
        """Safely get profile picture URL with proper Cloudinary support"""
        if not self.profile_picture:
            print(f"DEBUG: No profile picture set for user {self.username}")
            return None

        try:
            # Use Django's storage backend to generate the URL
            # This should work for both local filesystem and Cloudinary
            url = self.profile_picture.url
            print(f"DEBUG: Storage URL: {url}")
            return url
        except (ValueError, AttributeError, OSError) as e:
            print(f"DEBUG: Error getting URL: {str(e)}")
            return None
