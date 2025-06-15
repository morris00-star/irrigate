import os
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_protect
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .utils import send_brevo_transactional_email


def home(request):
    return render(request, 'accounts/home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                # Handle profile picture update
                if 'profile_picture' in request.FILES:
                    # Delete old profile picture if it exists
                    if request.user.profile_picture:
                        try:
                            old_file_path = request.user.profile_picture.path
                            if os.path.exists(old_file_path):
                                default_storage.delete(old_file_path)
                        except Exception as e:
                            print(f"Error deleting old profile picture: {e}")

                # Save the form
                user = form.save()

                # Return appropriate response based on request type
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Profile updated successfully',
                        'profile_picture_url': user.profile_picture.url if user.profile_picture else None
                    })

                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Form validation failed',
                    'errors': form.errors
                }, status=400)
            messages.error(request, 'Please correct the errors below.')

    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'accounts/delete_account.html')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(email=email)
            if associated_users.exists():
                current_site = get_current_site(request)
                for user in associated_users:
                    subject = "Password Reset Request"
                    email_template = "accounts/password_reset_email.html"

                    context = {
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': current_site.name,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }

                    email_content = render_to_string(email_template, context)

                    # Use Brevo API to send email
                    if send_brevo_transactional_email(user.email, subject, email_content):
                        return redirect("password_reset_done")
                    else:
                        messages.error(request, "Failed to send password reset email. Please try again later.")
                        return redirect("password_reset")

            # Always return success to prevent email enumeration
            return redirect("password_reset_done")

    else:
        form = PasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form})


@login_required
def confirm_token_regeneration(request):
    return render(request, 'accounts/confirm_token_regeneration.html')


@require_POST
@csrf_protect
@login_required
def regenerate_api_key(request):
    if 'confirm' not in request.POST:
        # If not confirmed, redirect to confirmation page
        return redirect('confirm_token_regeneration')

    if request.POST['confirm'] == 'yes':
        # Delete the old token
        Token.objects.filter(user=request.user).delete()
        # Create a new token
        new_token = Token.objects.create(user=request.user)

        # If AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'API token regenerated successfully',
                'new_api_token': new_token.key
            })

        # For regular form submission
        messages.success(request, 'Your API token has been regenerated successfully.')
        return redirect('profile')

    # If confirmation was 'no'
    messages.info(request, 'Token regeneration cancelled. Your current token remains active.')
    return redirect('profile')

