import os
from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, validate_phone_number
import phonenumbers
from django.core.validators import RegexValidator


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

                # RESET THE FILE POINTER after verify()
                profile_picture.seek(0)

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
                # Check for double extensions
                filename = profile_picture.name
                if self.has_double_extension(filename):
                    raise forms.ValidationError(
                        "Filename contains double extensions. Please upload a file with a valid name.")


            except Exception as e:
                raise forms.ValidationError("Invalid image file")
        return profile_picture


    def has_double_extension(self, filename):
        """Check if filename has double extensions"""
        import os
        basename = os.path.basename(filename)
        name_parts = basename.split('.')

        # If there are more than 2 parts and the last parts are image extensions
        if len(name_parts) > 2:
            extensions = ['jpg', 'jpeg', 'png', 'gif']
            if name_parts[-1].lower() in extensions and name_parts[-2].lower() in extensions:
                return True
        return False


class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['sms_notification_frequency', 'receive_sms_alerts']
        widgets = {
            'sms_notification_frequency': forms.Select(choices=CustomUser.SMS_NOTIFICATION_CHOICES),
            'receive_sms_alerts': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the checkbox is unchecked by default for new users
        if not self.instance.pk:  # New user
            self.initial['receive_sms_alerts'] = False


class SMSVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit code.')],
        widget=forms.TextInput(attrs={
            'placeholder': '123456',
            'class': 'form-control',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={
            'placeholder': '+256712345678',
            'class': 'form-control'
        })
    )

