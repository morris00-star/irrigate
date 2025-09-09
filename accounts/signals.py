from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from smart_irrigation import settings
from .models import CustomUser
from django.core.files.storage import default_storage
import os


@receiver(pre_save, sender=CustomUser)
def check_profile_picture_exists(sender, instance, **kwargs):
    """Check if profile picture exists before saving"""
    if instance.profile_picture:
        # Check if the file actually exists in storage
        if not default_storage.exists(instance.profile_picture.name):
            print(f"DEBUG: Profile picture does not exist: {instance.profile_picture.name}")
            instance.profile_picture = None


@receiver(post_save, sender=CustomUser)
def handle_profile_picture_changes(sender, instance, created, **kwargs):
    """Handle profile picture changes after saving"""
    if not created:
        try:
            # Get the previous state
            old_user = CustomUser.objects.get(pk=instance.pk)

            # Check if profile picture was changed
            if old_user.profile_picture != instance.profile_picture:
                print(f"DEBUG: Profile picture changed for user {instance.username}")

                # Handle old file deletion for local development
                if (old_user.profile_picture and
                        not settings.IS_PRODUCTION):
                    try:
                        if os.path.isfile(old_user.profile_picture.path):
                            os.remove(old_user.profile_picture.path)
                            print(f"DEBUG: Deleted old profile picture: {old_user.profile_picture.path}")
                    except (ValueError, AttributeError, OSError):
                        pass
        except CustomUser.DoesNotExist:
            pass

