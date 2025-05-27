import os
import phonenumbers
import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField


def validate_phone_number(value):
    try:
        phone_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError("Invalid phone number")
    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError("Invalid phone number format")


class CustomUser(AbstractUser):
    # Cloudinary configuration for profile pictures
    profile_picture = CloudinaryField(
        'image',
        folder='profile_pics/',
        transformation=[
            {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
            {'quality': 'auto'}
        ],
        default='profile_pics/default_profile',  # Set your default image in Cloudinary
        blank=True,
        null=True,
        help_text="User profile picture"
    )

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

        # If profile picture is being updated and already exists in Cloudinary
        if self.pk and self.profile_picture:
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                if old_user.profile_picture and old_user.profile_picture.public_id != self.profile_picture.public_id:
                    # Delete old image from Cloudinary
                    from cloudinary.uploader import destroy
                    destroy(old_user.profile_picture.public_id)
            except CustomUser.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the profile picture from Cloudinary when user is deleted
        if self.profile_picture:
            from cloudinary.uploader import destroy
            try:
                destroy(self.profile_picture.public_id)
            except Exception:
                # Handle case where image might already be deleted
                pass
        super().delete(*args, **kwargs)

    @property
    def profile_picture_url(self):
        """Returns the URL of the profile picture with a default fallback"""
        if self.profile_picture:
            return self.profile_picture.url
        return "https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/v123/profile_pics/default_profile.jpg"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


def user_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'profile_pics/user_{instance.id}.{ext}'
    return filename
