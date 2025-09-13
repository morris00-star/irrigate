import os
import phonenumbers
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from smart_irrigation import settings
from .utils import get_cloudinary_url


def user_profile_path(instance, filename):
    """Generate path for user profile pictures"""
    # Get the file extension
    ext = os.path.splitext(filename)[1].lower()

    # Remove any existing extensions from the filename
    base_filename = os.path.splitext(filename)[0]
    base_filename = f'user_{instance.id}'

    # Create the new filename
    filename = f'profile_pics/{base_filename}{ext}'

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

    sms_alert_frequency = models.CharField(
        max_length=10,
        choices=[('immediate', 'Immediate'), ('hourly', 'Hourly'), ('daily', 'Daily')],
        default='immediate'
    )

    sms_alert_threshold = models.PositiveIntegerField(
        default=30,
        help_text="Moisture level threshold for sending alerts (%)"
    )
    quiet_hours_start = models.TimeField(
        default='22:00',  # 10 PM
        help_text="Start time for quiet hours (no alerts)"
    )
    quiet_hours_end = models.TimeField(
        default='06:00',  # 6 AM
        help_text="End time for quiet hours (no alerts)"
    )

    # SMS notification frequency
    SMS_NOTIFICATION_CHOICES = [
        (5, '5 seconds'),
        (10, '10 seconds'),
        (15, '15 seconds'),
        (30, '30 seconds'),
        (45, '45 seconds'),
        (60, '60 seconds'),
    ]

    sms_notification_frequency = models.IntegerField(
        choices=SMS_NOTIFICATION_CHOICES,
        default=15,
        help_text="Frequency for SMS notifications in seconds"
    )

    last_notification_sent = models.DateTimeField(null=True, blank=True)

    last_sms_alert = models.DateTimeField(null=True, blank=True)

    receive_sms_alerts = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['receive_sms_alerts', 'last_sms_alert']),
            models.Index(fields=['phone_number']),
        ]


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

        # Don't check file existence during upload - Cloudinary handles this
        # Only check in development and only if we're not uploading a new file
        if (self.profile_picture and
                hasattr(self.profile_picture, 'name') and
                not settings.IS_PRODUCTION and
                not getattr(self, '_uploading_profile_picture', False)):  # Add a flag to track uploads
            # Check if the file actually exists in local storage
            if not default_storage.exists(self.profile_picture.name):
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
            # This should automatically handle Cloudinary vs local storage
            url = self.profile_picture.url
            print(f"DEBUG: Storage URL: {url}")
            return url
        except (ValueError, AttributeError, OSError) as e:
            print(f"DEBUG: Error getting URL: {str(e)}")
            return None

    def can_receive_alert_now(self):
        """Check if user can receive alerts based on preferences and quiet hours"""
        if not self.receive_sms_alerts or not self.phone_number:
            return False

        # Check quiet hours
        now = timezone.now().time()
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Quiet hours don't cross midnight
            if self.quiet_hours_start <= now <= self.quiet_hours_end:
                return False
        else:
            # Quiet hours cross midnight
            if now >= self.quiet_hours_start or now <= self.quiet_hours_end:
                return False

        # Check frequency limits
        if self.last_sms_alert:
            time_since_last_alert = timezone.now() - self.last_sms_alert
            if self.sms_alert_frequency == 'hourly' and time_since_last_alert.total_seconds() < 3600:
                return False
            elif self.sms_alert_frequency == 'daily' and time_since_last_alert.total_seconds() < 86400:
                return False

        return True

    def update_last_alert_time(self):
        """Update the last alert timestamp"""
        self.last_sms_alert = timezone.now()
        self.save(update_fields=['last_sms_alert'])
