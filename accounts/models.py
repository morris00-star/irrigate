import os
import phonenumbers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings


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
        help_text="Format: +[country code][number]"
    )
    receive_sms_alerts = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Check if this is a new user or profile picture is being updated
        if self.pk:
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                if (old_user.profile_picture and
                        self.profile_picture and
                        old_user.profile_picture != self.profile_picture):
                    # Profile picture is being changed
                    self._delete_old_profile_picture(old_user.profile_picture)
            except CustomUser.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Create a token for the user when they're created
        if not hasattr(self, 'auth_token'):
            Token.objects.create(user=self)

    def _delete_old_profile_picture(self, old_picture):
        """Safely delete old profile picture"""
        try:
            if not settings.IS_PRODUCTION:
                # Local development - delete file from filesystem
                if old_picture and os.path.isfile(old_picture.path):
                    os.remove(old_picture.path)
            else:
                # Production - Cloudinary handles file management automatically
                # Old files are automatically replaced when new ones are uploaded
                pass
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
        """Safely get profile picture URL"""
        if not self.profile_picture:
            return None

        try:
            return self.profile_picture.url
        except (ValueError, AttributeError):
            return None
