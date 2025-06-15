import os
import phonenumbers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


def user_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'profile_pics/user_{instance.id}.{ext}'
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
        help_text="Format: +[country code][number]"
    )
    receive_sms_alerts = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create a token for the user when they're created
        if not hasattr(self, 'auth_token'):
            Token.objects.create(user=self)

    def delete(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('profile')
