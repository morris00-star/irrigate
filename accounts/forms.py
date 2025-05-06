import os
from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture', 'location', 'age')


    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            try:
                # Open the image to verify it's valid
                img = Image.open(profile_picture)
                img.verify()

                # Check file size (limit to 5MB)
                if profile_picture.size > 10 * 1024 * 1024:
                    raise forms.ValidationError("Image file too large ( > 10MB )")

                # Check file extension
                ext = os.path.splitext(profile_picture.name)[1]
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                if not ext.lower() in valid_extensions:
                    raise forms.ValidationError("Unsupported file extension. Please use .jpg, .jpeg, .png, or .gif")

                return profile_picture
            except Exception as e:
                raise forms.ValidationError("Invalid image file")
        return profile_picture


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'profile_picture', 'location', 'age')


    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            try:
                # Open the image to verify it's valid
                img = Image.open(profile_picture)
                img.verify()

                # Check file size (limit to 5MB)
                if profile_picture.size > 10 * 1024 * 1024:
                    raise forms.ValidationError("Image file too large ( > 10MB )")

                # Check file extension
                ext = os.path.splitext(profile_picture.name)[1]
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                if not ext.lower() in valid_extensions:
                    raise forms.ValidationError("Unsupported file extension. Please use .jpg, .jpeg, .png, or .gif")

                return profile_picture
            except Exception as e:
                raise forms.ValidationError("Invalid image file")
        return profile_picture

