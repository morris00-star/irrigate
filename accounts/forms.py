import os
from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
import phonenumbers


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture', 'location', 'age', 'phone_number')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            try:
                parsed_number = phonenumbers.parse(phone_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise forms.ValidationError("Invalid phone number")
                return phonenumbers.format_number(
                    parsed_number,
                    phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                raise forms.ValidationError("Invalid phone number format")
        return phone_number

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            try:
                # Open the image to verify it's valid
                img = Image.open(profile_picture)
                img.verify()

                # Check file size (limit to 10MB)
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
        fields = ('email', 'first_name', 'last_name', 'profile_picture', 'location', 'age', 'phone_number')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            try:
                parsed_number = phonenumbers.parse(phone_number, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise forms.ValidationError("Invalid phone number, start with country code:")
                return phonenumbers.format_number(
                    parsed_number,
                    phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                raise forms.ValidationError("Invalid phone number, start with country code:")
        return phone_number

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
